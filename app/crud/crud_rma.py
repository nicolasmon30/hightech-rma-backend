from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.rma import RMA, RMAStatus, RMAHistory
from app.models.rma_item import RMAItem
from app.models.user import User, UserRole
from app.schemas.rma import RMACreate, RMAUpdate
from app.core.utils import generate_rma_number
from app.services.email_service import email_service


class CRUDRMA(CRUDBase[RMA, RMACreate, RMAUpdate]):
    """
    Operaciones CRUD para RMA
    """
    
    def create_with_user(
        self, 
        db: Session, 
        *, 
        obj_in: RMACreate, 
        user_id: int,
        country_id: int
    ) -> RMA:
        """
        Crear RMA sin número (se generará al aprobar)
        """
        # Crear RMA principal sin rma_number (será None hasta que se apruebe)
        db_obj = RMA(
            rma_number=None,  # Se generará al aprobar
            company_name=obj_in.company_name,
            company_address=obj_in.company_address,
            postal_code=obj_in.postal_code,
            created_by=user_id,
            country_id=country_id,
            status=RMAStatus.RMA_SUBMITTED
        )
        
        db.add(db_obj)
        db.flush()  # Para obtener el ID sin hacer commit
        
        # Crear los items del RMA
        for item_data in obj_in.items:
            rma_item = RMAItem(
                rma_id=db_obj.id,
                brand_id=item_data.brand_id,
                product_id=item_data.product_id,
                model_id=item_data.model_id,
                serial_number=item_data.serial_number,
                service_type=item_data.service_type,
                issue_description=item_data.issue_description
            )
            db.add(rma_item)
        
        # Crear entrada en historial ANTES del commit
        self._create_history(
            db, 
            rma_id=db_obj.id, 
            new_status=RMAStatus.RMA_SUBMITTED,
            user_id=user_id,
            old_status=None,  # No hay estado anterior cuando se crea
            comment="RMA creado"
        )
        
        # Ahora hacer commit de todo junto
        db.commit()
        db.refresh(db_obj)
        
        # Enviar email al usuario
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                email_service.send_rma_created_email(
                    user_email=user.email,
                    user_name=user.full_name,
                    company_name=db_obj.company_name,
                    items_count=len(db_obj.items),
                    rma_id=db_obj.id
                )
        except Exception as e:
            print(f"⚠️ Error enviando email de RMA creado: {e}")
        
        return db_obj
    
    def update_status(
        self,
        db: Session,
        *,
        rma: RMA,
        new_status: RMAStatus,
        user_id: int,
        comment: Optional[str] = None,
        shipping_company: Optional[str] = None,
        tracking_id: Optional[str] = None
    ) -> RMA:
        """
        Actualizar estado del RMA y registrar en historial.
        Genera rma_number automáticamente cuando se aprueba.
        Envía emails según el nuevo estado.
        Gestiona recordatorios automáticos de pago.
        """
        old_status = rma.status
        
        # Si el nuevo estado es APPROVED y no tiene rma_number, generarlo
        if new_status == RMAStatus.APPROVED and not rma.rma_number:
            rma.rma_number = generate_rma_number(db, rma.country_id)
        
        # Si el nuevo estado es IN_SHIPPING, guardar datos de envío
        if new_status == RMAStatus.IN_SHIPPING:
            rma.shipping_company = shipping_company
            rma.tracking_id = tracking_id
        
        # Gestión de recordatorios de pago
        # Si sale del estado PAYMENT, resetear el contador de recordatorios
        if old_status == RMAStatus.PAYMENT and new_status != RMAStatus.PAYMENT:
            rma.last_payment_reminder = None
            print(f"🔕 Recordatorios de pago detenidos para RMA {rma.rma_number or rma.id}")
        
        # Crear entrada en historial ANTES de cambiar el estado
        # Esto asegura que old_status se guarde correctamente
        self._create_history(
            db,
            rma_id=rma.id,
            new_status=new_status,
            user_id=user_id,
            old_status=old_status,
            comment=comment
        )
        
        # Ahora sí, actualizar el estado
        rma.status = new_status
        
        db.commit()
        db.refresh(rma)
        
        # Enviar email según el nuevo estado
        self._send_status_change_email(db, rma, new_status, comment)
        
        return rma
    
    def _send_status_change_email(
        self,
        db: Session,
        rma: RMA,
        new_status: RMAStatus,
        comment: Optional[str] = None
    ):
        """Enviar email cuando cambia el estado del RMA"""
        try:
            # Obtener usuario creador
            user = db.query(User).filter(User.id == rma.created_by).first()
            if not user:
                return
            
            # Mapeo de estados a nombres legibles
            status_display_names = {
                RMAStatus.RMA_SUBMITTED: "Solicitud Enviada",
                RMAStatus.AWAITING_GOODS: "Esperando Productos",
                RMAStatus.EVALUATING: "En Evaluación",
                RMAStatus.PROCESSING: "En Procesamiento",
                RMAStatus.PAYMENT: "Pago Pendiente",
                RMAStatus.IN_REPAIR: "En Reparación",
                RMAStatus.APPROVED: "Aprobado",
                RMAStatus.REJECTED: "Rechazado",
                RMAStatus.IN_SHIPPING: "En Envío",
                RMAStatus.COMPLETED: "Completado"
            }
            
            status_display = status_display_names.get(new_status, new_status.value)
            
            # Estados con emails específicos (mantener los existentes)
            if new_status == RMAStatus.APPROVED:
                email_service.send_rma_approved_email(
                    user_email=user.email,
                    user_name=user.full_name,
                    rma_number=rma.rma_number,
                    company_name=rma.company_name,
                    comment=comment
                )
            
            elif new_status == RMAStatus.REJECTED:
                reason = comment or "No se proporcionó un motivo específico"
                email_service.send_rma_rejected_email(
                    user_email=user.email,
                    user_name=user.full_name,
                    company_name=rma.company_name,
                    rma_id=rma.id,
                    reason=reason
                )
            
            elif new_status == RMAStatus.IN_SHIPPING:
                if rma.shipping_company and rma.tracking_id:
                    email_service.send_rma_shipping_email(
                        user_email=user.email,
                        user_name=user.full_name,
                        rma_number=rma.rma_number or f"RMA #{rma.id}",
                        company_name=rma.company_name,
                        shipping_company=rma.shipping_company,
                        tracking_id=rma.tracking_id
                    )
                else:
                    # Si no hay datos de shipping, enviar email genérico
                    email_service.send_rma_status_change_email(
                        user_email=user.email,
                        user_name=user.full_name,
                        rma_number=rma.rma_number,
                        company_name=rma.company_name,
                        new_status=new_status.value,
                        status_display=status_display,
                        comment=comment
                    )
            
            elif new_status == RMAStatus.COMPLETED:
                email_service.send_rma_completed_email(
                    user_email=user.email,
                    user_name=user.full_name,
                    rma_number=rma.rma_number or f"RMA #{rma.id}",
                    company_name=rma.company_name,
                    comment=comment
                )
            
            # TODOS los demás estados: enviar email genérico
            else:
                email_service.send_rma_status_change_email(
                    user_email=user.email,
                    user_name=user.full_name,
                    rma_number=rma.rma_number,
                    company_name=rma.company_name,
                    new_status=new_status.value,
                    status_display=status_display,
                    comment=comment
                )
        
        except Exception as e:
            print(f"⚠️ Error enviando email de cambio de estado: {e}")
    
    def _create_history(
        self,
        db: Session,
        *,
        rma_id: int,
        new_status: RMAStatus,
        user_id: int,
        old_status: Optional[RMAStatus] = None,
        comment: Optional[str] = None
    ) -> RMAHistory:
        """
        Crear entrada en historial
        """
        history = RMAHistory(
            rma_id=rma_id,
            previous_status=old_status,
            new_status=new_status,
            changed_by=user_id,
            comment=comment
        )
        db.add(history)
        # NO hacer commit aquí, se hará en el método que llama
        db.flush()  # Flush para obtener el ID pero sin commit
        return history
    
    def get_by_user(self, db: Session, *, user_id: int) -> List[RMA]:
        """
        Obtener RMAs creados por un usuario
        """
        return db.query(RMA).filter(RMA.created_by == user_id).all()
    
    def get_by_country(self, db: Session, *, country_id: int) -> List[RMA]:
        """
        Obtener RMAs de un país
        """
        return db.query(RMA).filter(RMA.country_id == country_id).all()
    
    def get_by_status(self, db: Session, *, status: RMAStatus) -> List[RMA]:
        """
        Obtener RMAs por estado
        """
        return db.query(RMA).filter(RMA.status == status).all()


rma = CRUDRMA(RMA)