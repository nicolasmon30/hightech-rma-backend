from pydantic import BaseModel
from typing import Optional
from app.models.user import UserRole


class Token(BaseModel):
    """Token de acceso JWT"""
    access_token: str
    token_type: str = "bearer"
    user: Optional[dict] = None


class TokenData(BaseModel):
    """Datos decodificados del token"""
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None