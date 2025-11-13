from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.core.security import create_access_token
from app.core.validators import validate_password_strength
from app.crud import user as crud_user
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import Token
from app.api.deps import get_current_active_user
from app.models.user import User
from app.services.email_service import email_service

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate
) -> Any:
    """
    Registrar nuevo usuario (cliente externo)
    """
    # Verificar si el email ya existe
    user = crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )

    # Validar fortaleza de contraseña
    is_valid, error_msg = validate_password_strength(user_in.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    # Crear usuario
    user = crud_user.create(db, obj_in=user_in)
    
    # Enviar email de bienvenida
    try:
        email_service.send_welcome_email(
            user_email=user.email,
            user_name=user.full_name
        )
    except Exception as e:
        # No fallar el registro si el email falla
        print(f"⚠️ Error enviando email de bienvenida: {e}")
    
    return user


@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Login con email y contraseña
    Retorna token JWT
    """
    # Autenticar usuario
    user = crud_user.authenticate(
        db,
        email=form_data.username,  # OAuth2 usa 'username' pero enviamos email
        password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )

    # Crear token
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)


    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role.value},  # ✅ Convertir a string
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/test-token", response_model=UserResponse)
def test_token(
    current_user: User = Depends(get_current_active_user)  # ✅ CORREGIDO
) -> Any:
    """
    Probar token de acceso.
    Retorna información del usuario actual si el token es válido.
    """
    return current_user
