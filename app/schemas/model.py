from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class ModelBase(BaseModel):
    """Campos base de Model"""
    name: str = Field(..., min_length=1, max_length=255)
    
    # Solución al warning
    model_config = ConfigDict(protected_namespaces=())


class ModelCreate(ModelBase):
    """Schema para crear modelo"""
    product_id: int = Field(..., gt=0)


class ModelUpdate(BaseModel):
    """Schema para actualizar modelo"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_active: Optional[bool] = None
    
    model_config = ConfigDict(protected_namespaces=())


class ModelResponse(ModelBase):
    """Schema de respuesta de Model"""
    id: int
    product_id: int
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class ModelWithProduct(ModelResponse):
    """Modelo con su producto"""
    product: "ProductWithBrand"
    
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


from app.schemas.product import ProductWithBrand
ModelWithProduct.model_rebuild()