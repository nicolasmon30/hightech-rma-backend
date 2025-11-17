from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.api.deps import (
    get_current_active_user,
    get_current_admin,
    check_user_country_access
)
from app.crud import rma as crud_rma
from app.crud import country as crud_country
from app.schemas.rma import (
    RMACreate,
    RMAResponse,
    RMAListResponse,
    RMAUpdate,
    RMAStatusUpdate
)
from app.models.user import User, UserRole
from app.models.rma import RMAStatus, RMA
from app.schemas.rma_history import RMAHistoryWithUser
from app.core.websocket import manager

router = APIRouter()


@router.post("", response_model=RMAResponse, status_code=status.HTTP_201_CREATED)
async def create_rma(
    *,
    db: Session = Depends(get_db),
    rma_in: RMACreate,
    country_id: int = Query(..., description="ID del país"),
    current_user: User = Depends(get_current_active_user),
    background_tasks: BackgroundTasks
) -> Any:
    """
    Crear nuevo RMA (USER/ADMIN/SUPERADMIN)
    
    - USER: Puede crear RMAs para sus países asignados
    - ADMIN: Puede crear RMAs para sus países
    - SUPERADMIN: Puede crear RMAs para cualquier país
    
    **Notificaciones en tiempo real:**
    - Se envía notificación WebSocket a SUPERADMIN (todos los RMAs)
    - Se envía notificación WebSocket a ADMIN del país del RMA
    """
    # Verificar que el país existe
    country = crud_country.get(db, id=country_id)
    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="País no encontrado"
        )
    
    # Verificar acceso al país
    if not check_user_country_access(current_user, country_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a este país"
        )
    
    # Crear RMA
    try:
        rma = crud_rma.create_with_user(
            db,
            obj_in=rma_in,
            user_id=current_user.id,
            country_id=country_id
        )
    except IntegrityError as e:
        db.rollback()
        # Mensaje claro para serial duplicado (a nivel DB)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un item con el mismo serial_number en otro RMA. Cambia el serial o edita el RMA anterior."
        ) from e
    
    # Serializar RMA para WebSocket
    rma_data = {
        "id": rma.id,
        "rma_number": rma.rma_number,
        "status": rma.status,
        "company_name": rma.company_name,
        "company_address": rma.company_address,
        "postal_code": rma.postal_code,
        "country_id": rma.country_id,
        "country_name": rma.country.name if rma.country else None,
        "created_by": rma.creator.email if rma.creator else None,
        "created_at": rma.created_at.isoformat() if rma.created_at else None,
        "total_items": len(rma.items) if rma.items else 0
    }
    
    # Enviar notificación WebSocket en background
    background_tasks.add_task(manager.notify_new_rma, rma_data, country_id)
    
    return rma


@router.get("", response_model=List[RMAResponse])
def get_rmas(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[RMAStatus] = None,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Obtener lista de RMAs
    
    - USER: Solo sus propios RMAs
    - ADMIN: RMAs de su país
    - SUPERADMIN: Todos los RMAs
    """
    if current_user.role == UserRole.SUPERADMIN:
        # Superadmin ve todos
        if status_filter:
            rmas = crud_rma.get_by_status(db, status=status_filter)
        else:
            rmas = crud_rma.get_multi(db, skip=skip, limit=limit)
    
    elif current_user.role == UserRole.ADMIN:
        # Admin ve los de su país
        rmas = []
        for country in current_user.countries:
            country_rmas = crud_rma.get_by_country(db, country_id=country.id)
            rmas.extend(country_rmas)
        
        # Filtrar por estado si se especifica
        if status_filter:
            rmas = [r for r in rmas if r.status == status_filter]
    
    else:  # USER
        # User solo ve los suyos
        rmas = crud_rma.get_by_user(db, user_id=current_user.id)
        
        # Filtrar por estado si se especifica
        if status_filter:
            rmas = [r for r in rmas if r.status == status_filter]
    
    return rmas[skip:skip+limit]


@router.get("/my-rmas", response_model=List[RMAResponse])
def get_my_rmas(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Obtener RMAs del usuario actual (todos los roles)
    """
    rmas = crud_rma.get_by_user(db, user_id=current_user.id)
    return rmas[skip:skip+limit]


@router.get("/country/{country_id}", response_model=List[RMAResponse])
def get_rmas_by_country(
    country_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin)  # Solo ADMIN/SUPERADMIN
) -> Any:
    """
    Obtener RMAs por país (ADMIN/SUPERADMIN)
    """
    # Verificar acceso al país
    if not check_user_country_access(current_user, country_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a este país"
        )
    
    rmas = crud_rma.get_by_country(db, country_id=country_id)
    return rmas[skip:skip+limit]


@router.get("/{rma_id}", response_model=RMAResponse)
def get_rma(
    rma_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Obtener RMA por ID
    
    - USER: Solo si es el creador
    - ADMIN: Si es de su país
    - SUPERADMIN: Cualquiera
    """
    rma = crud_rma.get(db, id=rma_id)
    if not rma:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RMA no encontrado"
        )
    
    # Verificar permisos
    if current_user.role == UserRole.USER:
        # User solo puede ver sus propios RMAs
        if rma.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a este RMA"
            )
    
    elif current_user.role == UserRole.ADMIN:
        # Admin solo puede ver RMAs de su país
        if not check_user_country_access(current_user, rma.country_id, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a este RMA"
            )
    
    # SUPERADMIN puede ver todo
    
    return rma


@router.put("/{rma_id}/status", response_model=RMAResponse)
async def update_rma_status(
    *,
    db: Session = Depends(get_db),
    rma_id: int,
    status_update: RMAStatusUpdate,
    current_user: User = Depends(get_current_admin),  # ADMIN/SUPERADMIN
    background_tasks: BackgroundTasks
) -> Any:
    """
    Actualizar estado de RMA (ADMIN/SUPERADMIN)
    
    - ADMIN: Solo RMAs de su país
    - SUPERADMIN: Cualquier RMA
    
    **Notificaciones en tiempo real:**
    - Se envía notificación WebSocket cuando cambia el estado
    """
    rma = crud_rma.get(db, id=rma_id)
    if not rma:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RMA no encontrado"
        )
    
    # Verificar permisos (admin solo puede actualizar RMAs de su país)
    if current_user.role == UserRole.ADMIN:
        if not check_user_country_access(current_user, rma.country_id, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a este RMA"
            )
    
    # Validar datos de envío si el estado es IN_SHIPPING
    if status_update.new_status == RMAStatus.IN_SHIPPING:
        if not status_update.shipping_company or not status_update.tracking_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="shipping_company y tracking_id son requeridos para estado IN_SHIPPING"
            )
    
    # Actualizar estado
    rma = crud_rma.update_status(
        db,
        rma=rma,
        new_status=status_update.new_status,
        user_id=current_user.id,
        comment=status_update.comment,
        shipping_company=status_update.shipping_company,
        tracking_id=status_update.tracking_id
    )
    
    # Serializar RMA para WebSocket
    rma_data = {
        "id": rma.id,
        "rma_number": rma.rma_number,
        "status": rma.status,
        "company_name": rma.company_name,
        "company_address": rma.company_address,
        "postal_code": rma.postal_code,
        "country_id": rma.country_id,
        "country_name": rma.country.name if rma.country else None,
        "updated_by": current_user.email,
        "updated_at": rma.updated_at.isoformat() if rma.updated_at else None,
        "shipping_company": rma.shipping_company,
        "tracking_id": rma.tracking_id,
        "total_items": len(rma.items) if rma.items else 0
    }
    
    # Enviar notificación WebSocket en background
    background_tasks.add_task(manager.notify_rma_status_change, rma_data, rma.country_id)
    
    return rma


@router.put("/{rma_id}", response_model=RMAResponse)
def update_rma(
    *,
    db: Session = Depends(get_db),
    rma_id: int,
    rma_in: RMAUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Actualizar información de RMA
    
    - USER: Solo sus propios RMAs y solo si están en estado RMA_SUBMITTED
    - ADMIN: RMAs de su país
    - SUPERADMIN: Cualquier RMA
    """
    rma = crud_rma.get(db, id=rma_id)
    if not rma:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RMA no encontrado"
        )
    
    # Verificar permisos
    if current_user.role == UserRole.USER:
        # User solo puede editar sus propios RMAs
        if rma.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a este RMA"
            )
        
        # Solo si está en estado inicial
        if rma.status != RMAStatus.RMA_SUBMITTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo puedes editar RMAs en estado 'RMA Submitted'"
            )
    
    elif current_user.role == UserRole.ADMIN:
        # Admin solo puede editar RMAs de su país
        if not check_user_country_access(current_user, rma.country_id, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a este RMA"
            )
    
    # Actualizar
    rma = crud_rma.update(db, db_obj=rma, obj_in=rma_in)
    
    return rma


@router.delete("/{rma_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rma(
    *,
    db: Session = Depends(get_db),
    rma_id: int,
    current_user: User = Depends(get_current_active_user)
) -> None:
    """
    Eliminar RMA
    
    - USER: Solo sus propios RMAs y solo si están en RMA_SUBMITTED
    - SUPERADMIN: Cualquier RMA
    - ADMIN: NO PUEDE ELIMINAR
    """
    rma = crud_rma.get(db, id=rma_id)
    if not rma:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RMA no encontrado"
        )
    
    # Verificar permisos
    if current_user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Los administradores no pueden eliminar RMAs"
        )
    
    if current_user.role == UserRole.USER:
        # User solo puede eliminar sus propios RMAs
        if rma.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a este RMA"
            )
        
        # Solo si está en estado inicial
        if rma.status != RMAStatus.RMA_SUBMITTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo puedes eliminar RMAs en estado 'RMA Submitted'"
            )
    
    # SUPERADMIN puede eliminar cualquiera
    
    crud_rma.delete(db, id=rma_id)


@router.get("/{rma_id}/history", response_model=List[RMAHistoryWithUser])  # ✅ Cambiar
def get_rma_history(
    rma_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Obtener historial de cambios de un RMA
    """
    rma = crud_rma.get(db, id=rma_id)
    if not rma:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RMA no encontrado"
        )
    
    # Verificar permisos (mismo que ver RMA)
    if current_user.role == UserRole.USER:
        if rma.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a este RMA"
            )
    
    elif current_user.role == UserRole.ADMIN:
        if not check_user_country_access(current_user, rma.country_id, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a este RMA"
            )
    
    return rma.history


@router.get("/stats/summary", response_model=dict)
def get_rma_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)  # ADMIN/SUPERADMIN
) -> Any:
    """
    Obtener estadísticas de RMAs (ADMIN/SUPERADMIN)
    
    - ADMIN: Estadísticas de su país
    - SUPERADMIN: Estadísticas globales
    """
    if current_user.role == UserRole.SUPERADMIN:
        # Estadísticas globales
        rmas = crud_rma.get_multi(db, skip=0, limit=100000)
    else:
        # Estadísticas del país del admin
        rmas = []
        for country in current_user.countries:
            rmas.extend(crud_rma.get_by_country(db, country_id=country.id))
    
    # Calcular estadísticas
    total = len(rmas)
    by_status = {}
    
    for status in RMAStatus:
        count = len([r for r in rmas if r.status == status])
        by_status[status.value] = count
    
    return {
        "total": total,
        "by_status": by_status,
        "countries": len(current_user.countries) if current_user.role != UserRole.SUPERADMIN else "all"
    }