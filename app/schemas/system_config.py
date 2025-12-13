from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class SystemConfigBase(BaseModel):
    """Schema base para configuración del sistema"""
    key: str = Field(..., description="Clave de configuración", min_length=1, max_length=100)
    value: str = Field(..., description="Valor de la configuración", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Descripción de la configuración", max_length=500)


class SystemConfigCreate(SystemConfigBase):
    """Schema para crear configuración"""
    pass


class SystemConfigUpdate(BaseModel):
    """Schema para actualizar configuración (solo el valor)"""
    value: str = Field(..., description="Nuevo valor de la configuración", min_length=1, max_length=255)


class SystemConfigResponse(SystemConfigBase):
    """Schema de respuesta para configuración"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PaymentReminderConfigUpdate(BaseModel):
    """Schema específico para actualizar configuración de recordatorios de pago"""
    payment_reminder_interval_days: int = Field(
        ..., 
        ge=1, 
        le=30,
        description="Días entre recordatorios de pago (1-30)"
    )
    payment_reminder_check_interval_hours: int = Field(
        ..., 
        ge=1, 
        le=168,
        description="Frecuencia de verificación en horas (1-168)"
    )


class PaymentReminderConfigResponse(BaseModel):
    """Schema de respuesta para configuración de recordatorios de pago"""
    payment_reminder_interval_days: int
    payment_reminder_check_interval_hours: int
