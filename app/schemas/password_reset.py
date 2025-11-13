"""
Schemas para recuperación de contraseña
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class PasswordResetRequest(BaseModel):
    """
    Schema para solicitar recuperación de contraseña
    Solo necesita el email
    """
    email: EmailStr = Field(..., description="Email del usuario que olvidó su contraseña")


class PasswordResetConfirm(BaseModel):
    """
    Schema para confirmar el reset con token y nueva contraseña
    """
    token: str = Field(..., description="Token de recuperación recibido por email")
    new_password: str = Field(..., min_length=6, description="Nueva contraseña (mínimo 6 caracteres)")


class PasswordResetResponse(BaseModel):
    """
    Schema de respuesta después de solicitar reset
    """
    message: str
    email: str


class PasswordResetConfirmResponse(BaseModel):
    """
    Schema de respuesta después de confirmar reset
    """
    message: str
    success: bool
