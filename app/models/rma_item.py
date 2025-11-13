"""
Modelo de Item de RMA
Cada RMA puede tener múltiples items (productos)
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class ServiceType(str, enum.Enum):
    """Tipos de servicio"""
    CALIBRATION = "calibration"         # Calibración
    BOTH = "both"  # Ambas
    REPAIR = "repair"             # Reparación


class RMAItem(Base):
    """
    Item individual dentro de un RMA
    Cada item representa un producto específico
    """
    __tablename__ = "rma_items"
    
    # Identificación
    id = Column(Integer, primary_key=True, index=True)
    
    # Relación con el RMA padre
    rma_id = Column(
        Integer, 
        ForeignKey("rmas.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Información del producto
    brand_id = Column(
        Integer,
        ForeignKey("brands.id", ondelete="RESTRICT"),
        nullable=False
    )
    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False
    )
    model_id = Column(
        Integer,
        ForeignKey("models.id", ondelete="RESTRICT"),
        nullable=False
    )
    
    # Serial único del producto
    serial_number = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True
    )
    
    # ⭐ Tipo de servicio por item
    service_type = Column(SQLEnum(ServiceType), nullable=False)
    
    # Descripción del problema específico de este producto
    issue_description = Column(Text, nullable=False)
    
    # Auditoría
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    rma = relationship("RMA", back_populates="items")
    brand = relationship("Brand")
    product = relationship("Product")
    model = relationship("Model")
    
    def __repr__(self):
        return f"<RMAItem {self.serial_number} - {self.service_type}>"