from sqlalchemy import Column, Integer, String, Boolean, DateTime, Table, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.associations import user_countries, brand_countries, shipping_company_countries  # Importar tablas intermedias




class Country(Base):
    """
    Países donde opera HighTech (USA, Colombia, etc.)
    """
    __tablename__ = "countries"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)  # "United States", "Colombia"
    code = Column(String(2), unique=True, nullable=False, index=True)    # "US", "CO"
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones (las definiremos después)
    rmas = relationship("RMA", back_populates="country")
    users = relationship(
        "User",
        secondary=user_countries,
        back_populates="countries"
    )
    brands = relationship(
        "Brand",
        secondary=brand_countries,
        back_populates="countries"
    )
    shipping_companies = relationship(
        "ShippingCompany",
        secondary=shipping_company_countries,
        back_populates="countries"
    )
    
    def __repr__(self):
        return f"<Country {self.name} ({self.code})>"