from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class BrandBase(BaseModel):
    """Campos base de Brand"""
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=500)


class BrandCreate(BrandBase):
    """Schema para crear marca"""
    country_ids: List[int] = Field(..., min_items=1, description="IDs de países donde está disponible")


class BrandUpdate(BaseModel):
    """Schema para actualizar marca"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    country_ids: Optional[List[int]] = None
    is_active: Optional[bool] = None


class BrandResponse(BrandBase):
    """Schema de respuesta de Brand"""
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class BrandWithCountries(BrandResponse):
    """Marca con sus países"""
    countries: List["CountryResponse"]
    
    class Config:
        from_attributes = True


from app.schemas.country import CountryResponse
BrandWithCountries.model_rebuild()