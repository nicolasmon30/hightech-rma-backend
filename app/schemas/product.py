from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):
    """Campos base de Product"""
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=500)


class ProductCreate(ProductBase):
    """Schema para crear producto"""
    brand_id: int = Field(..., gt=0)


class ProductUpdate(BaseModel):
    """Schema para actualizar producto"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    """Schema de respuesta de Product"""
    id: int
    brand_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProductWithBrand(ProductResponse):
    """Producto con su marca"""
    brand: "BrandResponse"
    
    class Config:
        from_attributes = True


from app.schemas.brand import BrandResponse
ProductWithBrand.model_rebuild()