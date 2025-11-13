from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.associations import shipping_company_countries


class ShippingCompany(Base):
    """
    Empresas transportadoras (DHL, FedEx, UPS, etc.)
    Pueden operar en uno o varios países
    """
    __tablename__ = "shipping_companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    countries = relationship(
        "Country",
        secondary=shipping_company_countries,
        back_populates="shipping_companies"
    )
    
    def __repr__(self):
        return f"<ShippingCompany {self.name}>"
