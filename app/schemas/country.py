from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CountryBase(BaseModel):
    """Campos base de Country"""
    name: str = Field(..., min_length=2, max_length=100, description="Nombre del país")
    code: str = Field(..., min_length=3, max_length=3, description="Código ISO (USA, COL)")


class CountryCreate(CountryBase):
    """Schema para crear un país"""
    pass


class CountryUpdate(BaseModel):
    """Schema para actualizar un país"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    is_active: Optional[bool] = None


class CountryResponse(CountryBase):
    """Schema de respuesta de Country"""
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True  # Permite convertir modelos SQLAlchemy a Pydantic