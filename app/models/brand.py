from sqlalchemy import Column, Integer, String, Boolean, DateTime, Table, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.associations import brand_countries  # Importar tabla intermedia


class Brand(Base):
    """
    Marcas de productos (Fluke, Olympus, etc.)
    Pueden estar disponibles en uno o varios países
    """
    __tablename__ = "brands"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(String(500), nullable=True)  # Descripción de la marca
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    countries = relationship(
        "Country",
        secondary=brand_countries,
        back_populates="brands"
    )
    products = relationship("Product", back_populates="brand", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Brand {self.name}>"