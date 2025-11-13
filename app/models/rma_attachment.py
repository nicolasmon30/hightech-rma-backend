"""
Modelo de Adjuntos de RMA
Maneja PDFs de cotizaciones y facturas con versionado
"""
from sqlalchemy import Column, Integer, String, Enum as SQLEnum, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class AttachmentType(str, enum.Enum):
    """Tipos de documentos permitidos"""
    QUOTE = "quote"           # Cotizaciones
    INVOICE = "invoice"       # Facturas


class RMAAttachment(Base):
    """
    Modelo para almacenar adjuntos PDF de RMAs
    Soporta versionado: cada reemplazo crea una nueva versión
    """
    __tablename__ = "rma_attachments"
    
    # Identificación
    id = Column(Integer, primary_key=True, index=True)
    rma_id = Column(Integer, ForeignKey("rmas.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Tipo de documento
    attachment_type = Column(SQLEnum(AttachmentType), nullable=False, index=True)
    
    # Información del archivo
    original_filename = Column(String(255), nullable=False)  # "cotizacion_cliente.pdf"
    stored_filename = Column(String(255), nullable=False, unique=True)  # "rma-123-quote-v2-abc456.pdf"
    file_path = Column(String(500), nullable=False)  # Ruta completa en MinIO
    file_size = Column(Integer, nullable=False)  # Tamaño en bytes
    mime_type = Column(String(100), default="application/pdf", nullable=False)
    
    # Versionado
    version = Column(Integer, default=1, nullable=False)  # 1, 2, 3...
    is_latest = Column(Boolean, default=True, nullable=False, index=True)  # ¿Es la versión actual?
    replaced_by = Column(Integer, ForeignKey("rma_attachments.id"), nullable=True)  # ID del que lo reemplazó
    
    # Auditoría
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    description = Column(Text, nullable=True)  # Descripción opcional
    
    # Relaciones
    rma = relationship("RMA", back_populates="attachments")
    uploader = relationship("User", foreign_keys=[uploaded_by])
    
    # Autorreferencia para el versionado
    next_version = relationship(
        "RMAAttachment",
        foreign_keys=[replaced_by],
        remote_side=[id],
        uselist=False
    )
    
    def __repr__(self):
        return f"<RMAAttachment {self.attachment_type} v{self.version} for RMA#{self.rma_id}>"
