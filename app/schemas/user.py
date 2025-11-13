from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from app.models.user import UserRole, LanguageCode


class UserBase(BaseModel):
    """Campos base de User"""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    company: Optional[str] = Field(None, max_length=255)
    language: LanguageCode = LanguageCode.EN


class UserCreate(UserBase):
    """Schema para registro de usuario"""
    password: str = Field(..., min_length=8, max_length=100, description="Mínimo 8 caracteres")
    country_ids: List[int] = Field(..., min_items=1, description="IDs de países")


class UserCreateByAdmin(UserCreate):
    """Schema para que admin/superadmin cree usuarios"""
    role: UserRole = UserRole.USER


class UserLogin(BaseModel):
    """Schema para login"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema para actualizar usuario"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = None
    company: Optional[str] = None
    language: Optional[LanguageCode] = None
    country_ids: Optional[List[int]] = None


class UserUpdateByAdmin(UserUpdate):
    """Schema para que admin actualice usuarios"""
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserPasswordReset(BaseModel):
    """
    Schema para resetear contraseña por admin
    """
    new_password: str = Field(..., min_length=6, description="Nueva contraseña (mínimo 6 caracteres)")
    
    model_config = ConfigDict(from_attributes=True)


class UserListFilter(BaseModel):
    """
    Schema para filtrar usuarios
    """
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    country_id: Optional[int] = None
    search: Optional[str] = Field(None, description="Buscar por email, nombre o empresa")
    
    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    """Schema de respuesta de User (sin contraseña)"""
    id: int
    email: str
    full_name: str
    phone: Optional[str] = None
    company: Optional[str] = None
    language: LanguageCode
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True  # Serializar enums como strings
    )


class CountrySimple(BaseModel):
    """Schema simplificado de Country - solo para incluir en usuarios"""
    id: int
    name: str
    code: str
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)


class UserWithCountries(UserResponse):
    """Usuario con sus países - sin referencias circulares"""
    countries: List[CountrySimple] = []
    
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True  # Serializar enums como strings
    )