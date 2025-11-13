from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Product(Base):
    """
    Productos de una marca (Medidor de Espesor, etc.)
    """
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(String(500))
    is_active = Column(Boolean, default=True)
    
    # Relación con Marca
    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="CASCADE"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    brand = relationship("Brand", back_populates="products")
    models = relationship("Model", back_populates="product", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Product {self.name} (Brand: {self.brand_id})>"