"""
Schemas para Adjuntos de RMA
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.rma_attachment import AttachmentType


class AttachmentBase(BaseModel):
    """Base para adjuntos"""
    attachment_type: AttachmentType
    description: Optional[str] = Field(None, max_length=500)


class AttachmentUpload(AttachmentBase):
    """Schema para subir archivos - no incluye el file (va en UploadFile)"""
    pass


class AttachmentResponse(AttachmentBase):
    """Schema de respuesta completo"""
    id: int
    rma_id: int
    original_filename: str
    file_size: int
    version: int
    is_latest: bool
    uploaded_by: int
    uploaded_at: datetime
    
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class AttachmentHistory(BaseModel):
    """Schema para historial de versiones"""
    id: int
    version: int
    is_latest: bool
    uploaded_by: int
    uploaded_at: datetime
    file_size: int
    original_filename: str
    description: Optional[str]
    
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class AttachmentListItem(BaseModel):
    """Schema simplificado para listar"""
    id: int
    attachment_type: AttachmentType
    original_filename: str
    version: int
    is_latest: bool
    file_size: int
    uploaded_at: datetime
    
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())
