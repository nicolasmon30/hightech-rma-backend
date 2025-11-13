from sqlalchemy import Column, Integer, String, Enum as SQLEnum, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class RMAStatus(str, enum.Enum):
    """Estados del RMA"""
    RMA_SUBMITTED = "rma_submitted"
    AWAITING_GOODS = "awaiting_goods"
    EVALUATING = "evaluating"
    PROCESSING = "processing"
    PAYMENT = "payment"
    IN_SHIPPING = "in_shipping"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_REPAIR = "in_repair"
    COMPLETED = "completed"





class RMA(Base):
    """Modelo de RMA (Return Merchandise Authorization)"""
    __tablename__ = "rmas"
    
    id = Column(Integer, primary_key=True, index=True)
    rma_number = Column(String(20), unique=True, index=True, nullable=True)  # Se genera al aprobar
    
    # Información de la empresa
    company_name = Column(String(255), nullable=False)
    company_address = Column(String(500), nullable=False)
    postal_code = Column(String(20), nullable=False)
    
    # Información de envío (para estado IN_SHIPPING)
    shipping_company = Column(String(255), nullable=True)
    tracking_id = Column(String(255), nullable=True)
    
    # Recordatorio de pago (para estado PAYMENT)
    last_payment_reminder = Column(DateTime, nullable=True)
    
    # Estado y tracking
    status = Column(SQLEnum(RMAStatus), default=RMAStatus.RMA_SUBMITTED, nullable=False)
    
    # Auditoría
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    country = relationship("Country", back_populates="rmas")
    creator = relationship("User", foreign_keys=[created_by])
    
    # Relación con los items (productos) de este RMA
    items = relationship(
        "RMAItem",
        back_populates="rma",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    history = relationship("RMAHistory", back_populates="rma", cascade="all, delete-orphan")
    
    # Relación con adjuntos (PDFs)
    attachments = relationship(
        "RMAAttachment",
        back_populates="rma",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    def __repr__(self):
        return f"<RMA {self.rma_number}>"


class RMAHistory(Base):
    """Modelo para el historial de cambios de estado de RMA"""
    __tablename__ = "rma_history"
    
    id = Column(Integer, primary_key=True, index=True)
    rma_id = Column(Integer, ForeignKey("rmas.id", ondelete="CASCADE"), nullable=False)
    previous_status = Column(SQLEnum(RMAStatus), nullable=True)
    new_status = Column(SQLEnum(RMAStatus), nullable=False)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    comment = Column(String(500), nullable=True)
    
    # Relaciones
    rma = relationship("RMA", back_populates="history")
    changer = relationship("User", foreign_keys=[changed_by])
    
    def __repr__(self):
        return f"<RMAHistory RMA#{self.rma_id}: {self.previous_status} -> {self.new_status}>"