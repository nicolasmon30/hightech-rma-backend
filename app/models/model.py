from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Model(Base):
    """
    Modelos de un producto (45MG, EPOCH 650, etc.)
    """
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    
    # Relación con Producto
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    product = relationship("Product", back_populates="models")
    
    def __repr__(self):
        return f"<Model {self.name} (Product: {self.product_id})>"