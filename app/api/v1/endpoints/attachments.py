"""
Endpoints para adjuntos de RMA
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.deps import get_db, get_current_user
from app.models.user import User, UserRole
from app.models.rma import RMA
from app.models.rma_attachment import AttachmentType
from app.schemas.attachment import AttachmentResponse, AttachmentListItem, AttachmentHistory
from app.crud.crud_attachment import crud_attachment
from app.core.storage import download_file_from_minio
from app.services.email_service import email_service
from app.models.rma import RMAStatus


router = APIRouter()


def check_admin_or_superadmin(current_user: User) -> User:
    """Verificar que el usuario sea ADMIN o SUPERADMIN"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden gestionar adjuntos"
        )
    return current_user


def check_rma_access(db: Session, rma_id: int, current_user: User) -> RMA:
    """Verificar acceso al RMA según el país del usuario"""
    rma = db.query(RMA).filter(RMA.id == rma_id).first()
    
    if not rma:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RMA no encontrado"
        )
    
    # SUPERADMIN ve todos
    if current_user.role == UserRole.SUPERADMIN:
        return rma
    
    # ADMIN/USER solo ven de sus países asignados
    user_country_ids = [country.id for country in current_user.countries]
    if rma.country_id not in user_country_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene acceso a este RMA"
        )
    
    return rma


@router.post("/{rma_id}/attachments", response_model=AttachmentResponse, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    rma_id: int,
    file: UploadFile = File(...),
    attachment_type: AttachmentType = Form(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    📎 Subir nuevo adjunto a un RMA
    
    **Permisos:** Solo ADMIN y SUPERADMIN
    
    **Restricciones:**
    - Solo archivos PDF
    - Tamaño máximo: 2MB
    - Tipos: QUOTE o INVOICE
    """
    # Verificar permisos
    check_admin_or_superadmin(current_user)
    
    # Verificar acceso al RMA
    rma = check_rma_access(db, rma_id, current_user)
    
    # Leer contenido del archivo para adjuntar en email
    file.file.seek(0)
    file_content = await file.read()
    file.file.seek(0)  # Reset para que create_attachment pueda leerlo
    
    # Crear adjunto
    attachment = await crud_attachment.create_attachment(
        db=db,
        rma_id=rma_id,
        file=file,
        attachment_type=attachment_type,
        uploaded_by=current_user.id,
        description=description
    )
    
    # SIEMPRE enviar email cuando se sube cotización o factura
    try:
        creator = db.query(User).filter(User.id == rma.created_by).first()
        if creator:
            email_service.send_rma_quote_uploaded_email(
                user_email=creator.email,
                user_name=creator.full_name,
                rma_number=rma.rma_number,
                company_name=rma.company_name,
                attachment_type=attachment_type.value,
                comment=description,
                file_content=file_content,
                file_name=file.filename,
                language=creator.language.value
            )
            print(f"✅ Email de adjunto enviado a {creator.email} con PDF adjunto")
    except Exception as e:
        print(f"⚠️ Error enviando email de adjunto: {e}")
    
    return attachment


@router.put("/{rma_id}/attachments/{attachment_id}", response_model=AttachmentResponse)
async def replace_attachment(
    rma_id: int,
    attachment_id: int,
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🔄 Reemplazar adjunto existente (crea nueva versión)
    
    **Permisos:** Solo ADMIN y SUPERADMIN
    
    **Comportamiento:**
    - Mantiene historial de versiones anteriores
    - La versión anterior sigue accesible para consulta
    - Incrementa número de versión automáticamente
    """
    # Verificar permisos
    check_admin_or_superadmin(current_user)
    
    # Verificar acceso al RMA
    rma = check_rma_access(db, rma_id, current_user)
    
    # Leer contenido del archivo para adjuntar en email
    file.file.seek(0)
    file_content = await file.read()
    file.file.seek(0)  # Reset para que replace_attachment pueda leerlo
    
    # Reemplazar adjunto
    new_version = await crud_attachment.replace_attachment(
        db=db,
        attachment_id=attachment_id,
        file=file,
        uploaded_by=current_user.id,
        description=description
    )
    
    # Enviar email notificando la actualización con PDF adjunto
    try:
        creator = db.query(User).filter(User.id == rma.created_by).first()
        if creator:
            email_service.send_rma_quote_uploaded_email(
                user_email=creator.email,
                user_name=creator.full_name,
                rma_number=rma.rma_number,
                company_name=rma.company_name,
                attachment_type=new_version.attachment_type.value,
                comment=f"Documento actualizado (v{new_version.version}). {description or ''}",
                file_content=file_content,
                file_name=file.filename,
                language=creator.language.value
            )
            print(f"✅ Email de actualización de adjunto enviado a {creator.email} con PDF adjunto")
    except Exception as e:
        print(f"⚠️ Error enviando email de actualización: {e}")
    
    return new_version


@router.get("/{rma_id}/attachments", response_model=List[AttachmentListItem])
def list_attachments(
    rma_id: int,
    attachment_type: Optional[AttachmentType] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    📋 Listar adjuntos actuales de un RMA
    
    **Permisos:** Todos los usuarios (con acceso al RMA)
    
    **Query params:**
    - attachment_type: Filtrar por tipo (QUOTE o INVOICE)
    
    **Nota:** Solo muestra versiones actuales (is_latest=true)
    """
    # Verificar acceso al RMA
    check_rma_access(db, rma_id, current_user)
    
    # Obtener adjuntos
    attachments = crud_attachment.get_latest_by_rma(
        db=db,
        rma_id=rma_id,
        attachment_type=attachment_type
    )
    
    return attachments


@router.get("/{rma_id}/attachments/{attachment_id}/history", response_model=List[AttachmentHistory])
def get_attachment_history(
    rma_id: int,
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    📜 Obtener historial de versiones de un adjunto
    
    **Permisos:** Todos los usuarios (con acceso al RMA)
    
    **Retorna:** Todas las versiones ordenadas por número de versión (más reciente primero)
    """
    # Verificar acceso al RMA
    check_rma_access(db, rma_id, current_user)
    
    # Obtener adjunto para saber su tipo
    attachment = crud_attachment.get_by_id(db, attachment_id)
    if not attachment or attachment.rma_id != rma_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Adjunto no encontrado"
        )
    
    # Obtener historial
    history = crud_attachment.get_history(
        db=db,
        rma_id=rma_id,
        attachment_type=attachment.attachment_type
    )
    
    return history


@router.get("/{rma_id}/attachments/{attachment_id}/download")
async def download_attachment(
    rma_id: int,
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    ⬇️ Descargar adjunto
    
    **Permisos:** Todos los usuarios (con acceso al RMA)
    
    **Retorna:** Archivo PDF con headers apropiados para descarga
    """
    # Verificar acceso al RMA
    check_rma_access(db, rma_id, current_user)
    
    # Obtener adjunto
    attachment = crud_attachment.get_by_id(db, attachment_id)
    if not attachment or attachment.rma_id != rma_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Adjunto no encontrado"
        )
    
    # Descargar desde MinIO
    file_data = download_file_from_minio(attachment.file_path)
    
    return StreamingResponse(
        file_data,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{attachment.original_filename}"'
        }
    )


@router.delete("/{rma_id}/attachments/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attachment(
    rma_id: int,
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🗑️ Eliminar adjunto y todo su historial
    
    **Permisos:** Solo ADMIN y SUPERADMIN
    
    **Comportamiento:**
    - Elimina TODAS las versiones del adjunto
    - Elimina archivos físicos de MinIO
    - Operación irreversible
    """
    # Verificar permisos
    check_admin_or_superadmin(current_user)
    
    # Verificar acceso al RMA
    check_rma_access(db, rma_id, current_user)
    
    # Eliminar adjunto
    crud_attachment.delete_attachment(db=db, attachment_id=attachment_id)
    
    return None
