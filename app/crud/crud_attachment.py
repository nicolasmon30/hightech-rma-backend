"""
CRUD para Adjuntos de RMA con sistema de versionado
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import UploadFile, HTTPException, status
from typing import Optional
from datetime import datetime

from app.models.rma_attachment import RMAAttachment, AttachmentType
from app.models.rma import RMA
from app.core.storage import upload_file_to_minio, delete_file_from_minio


class CRUDAttachment:
    """CRUD para adjuntos de RMA"""
    
    async def create_attachment(
        self,
        db: Session,
        *,
        rma_id: int,
        file: UploadFile,
        attachment_type: AttachmentType,
        uploaded_by: int,
        description: Optional[str] = None
    ) -> RMAAttachment:
        """
        Crear nuevo adjunto (versión 1)
        """
        # Verificar que el RMA existe
        rma = db.query(RMA).filter(RMA.id == rma_id).first()
        if not rma:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="RMA no encontrado"
            )
        
        # Subir archivo a MinIO
        file_data = await upload_file_to_minio(file, rma_id)
        
        # Crear registro en BD
        db_attachment = RMAAttachment(
            rma_id=rma_id,
            attachment_type=attachment_type,
            original_filename=file.filename,
            stored_filename=file_data["stored_filename"],
            file_path=file_data["file_path"],
            file_size=file_data["file_size"],
            mime_type=file_data["mime_type"],
            version=1,
            is_latest=True,
            uploaded_by=uploaded_by,
            uploaded_at=datetime.utcnow(),
            description=description
        )
        
        db.add(db_attachment)
        db.commit()
        db.refresh(db_attachment)
        
        return db_attachment
    
    
    async def replace_attachment(
        self,
        db: Session,
        *,
        attachment_id: int,
        file: UploadFile,
        uploaded_by: int,
        description: Optional[str] = None
    ) -> RMAAttachment:
        """
        Reemplazar adjunto existente (crear nueva versión)
        """
        # Obtener adjunto actual
        current_attachment = db.query(RMAAttachment).filter(
            RMAAttachment.id == attachment_id,
            RMAAttachment.is_latest == True
        ).first()
        
        if not current_attachment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Adjunto no encontrado o no es la versión actual"
            )
        
        # Subir nuevo archivo
        file_data = await upload_file_to_minio(file, current_attachment.rma_id)
        
        # Crear nueva versión
        new_version = RMAAttachment(
            rma_id=current_attachment.rma_id,
            attachment_type=current_attachment.attachment_type,
            original_filename=file.filename,
            stored_filename=file_data["stored_filename"],
            file_path=file_data["file_path"],
            file_size=file_data["file_size"],
            mime_type=file_data["mime_type"],
            version=current_attachment.version + 1,
            is_latest=True,
            uploaded_by=uploaded_by,
            uploaded_at=datetime.utcnow(),
            description=description
        )
        
        # Marcar versión anterior como no actual
        current_attachment.is_latest = False
        current_attachment.replaced_by = new_version.id  # Se actualizará después del commit
        
        db.add(new_version)
        db.commit()
        db.refresh(new_version)
        
        # Actualizar replaced_by ahora que tenemos el ID
        current_attachment.replaced_by = new_version.id
        db.commit()
        
        return new_version
    
    
    def get_latest_by_rma(
        self,
        db: Session,
        rma_id: int,
        attachment_type: Optional[AttachmentType] = None
    ) -> list[RMAAttachment]:
        """
        Obtener adjuntos actuales de un RMA (solo versiones latest)
        """
        query = db.query(RMAAttachment).filter(
            RMAAttachment.rma_id == rma_id,
            RMAAttachment.is_latest == True
        )
        
        if attachment_type:
            query = query.filter(RMAAttachment.attachment_type == attachment_type)
        
        return query.order_by(RMAAttachment.uploaded_at.desc()).all()
    
    
    def get_history(
        self,
        db: Session,
        rma_id: int,
        attachment_type: AttachmentType
    ) -> list[RMAAttachment]:
        """
        Obtener historial completo de versiones de un tipo de adjunto
        """
        return db.query(RMAAttachment).filter(
            RMAAttachment.rma_id == rma_id,
            RMAAttachment.attachment_type == attachment_type
        ).order_by(RMAAttachment.version.desc()).all()
    
    
    def get_by_id(
        self,
        db: Session,
        attachment_id: int
    ) -> Optional[RMAAttachment]:
        """Obtener adjunto por ID (cualquier versión)"""
        return db.query(RMAAttachment).filter(
            RMAAttachment.id == attachment_id
        ).first()
    
    
    def delete_attachment(
        self,
        db: Session,
        attachment_id: int
    ) -> None:
        """
        Eliminar adjunto y todas sus versiones
        - Elimina archivos de MinIO
        - Si se elimina una versión intermedia, ajusta la cadena
        """
        attachment = self.get_by_id(db, attachment_id)
        
        if not attachment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Adjunto no encontrado"
            )
        
        # Obtener todas las versiones del mismo tipo
        all_versions = db.query(RMAAttachment).filter(
            RMAAttachment.rma_id == attachment.rma_id,
            RMAAttachment.attachment_type == attachment.attachment_type
        ).order_by(RMAAttachment.version).all()
        
        # Eliminar archivos físicos
        for version in all_versions:
            try:
                delete_file_from_minio(version.file_path)
            except Exception as e:
                print(f"⚠️ Error al eliminar archivo {version.file_path}: {e}")
        
        # Eliminar registros de BD
        for version in all_versions:
            db.delete(version)
        
        db.commit()
    
    
    def delete_specific_version(
        self,
        db: Session,
        attachment_id: int
    ) -> None:
        """
        Eliminar una versión específica (solo si no es la actual)
        """
        attachment = self.get_by_id(db, attachment_id)
        
        if not attachment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Adjunto no encontrado"
            )
        
        if attachment.is_latest:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar la versión actual. Use el endpoint de eliminación completa."
            )
        
        # Eliminar archivo físico
        delete_file_from_minio(attachment.file_path)
        
        # Ajustar cadena de versiones si es necesario
        if attachment.next_version:
            # Si hay una versión siguiente, actualizar su referencia
            next_version = attachment.next_version[0] if attachment.next_version else None
            if next_version:
                # La siguiente versión ya no apunta a esta
                pass  # La relación se maneja automáticamente
        
        db.delete(attachment)
        db.commit()


crud_attachment = CRUDAttachment()
