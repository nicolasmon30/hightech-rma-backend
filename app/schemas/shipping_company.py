from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ShippingCompanyBase(BaseModel):
    """Campos base de ShippingCompany"""
    name: str = Field(..., min_length=2, max_length=255)


class ShippingCompanyCreate(ShippingCompanyBase):
    """Schema para crear empresa transportadora"""
    country_ids: List[int] = Field(..., min_items=1, description="IDs de países donde opera")


class ShippingCompanyUpdate(BaseModel):
    """Schema para actualizar empresa transportadora"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    country_ids: Optional[List[int]] = None
    is_active: Optional[bool] = None


class ShippingCompanyResponse(ShippingCompanyBase):
    """Schema de respuesta de ShippingCompany"""
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ShippingCompanyWithCountries(ShippingCompanyResponse):
    """Empresa transportadora con sus países"""
    countries: List["CountryResponse"]
    
    class Config:
        from_attributes = True


from app.schemas.country import CountryResponse
ShippingCompanyWithCountries.model_rebuild()
