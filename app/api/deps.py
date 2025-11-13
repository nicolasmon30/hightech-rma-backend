from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserRole
from app.models.country import Country

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Obtiene el usuario actual desde el token JWT
    """
    print(f"🔍 DEBUG: Token recibido: {token[:50]}..." if token else "❌ No token")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decodificar token
    payload = decode_access_token(token)
    print(f"🔍 DEBUG: Payload decodificado: {payload}")
    
    if payload is None:
        print("❌ DEBUG: Payload es None")
        raise credentials_exception
    
    # Extraer user_id (viene como string del JWT)
    user_id_str = payload.get("sub")
    print(f"🔍 DEBUG: User ID (string) extraído: {user_id_str}")
    
    if user_id_str is None:
        print("❌ DEBUG: user_id_str es None")
        raise credentials_exception
    
    # Convertir a int
    try:
        user_id = int(user_id_str)
        print(f"🔍 DEBUG: User ID (int) convertido: {user_id}")
    except (ValueError, TypeError):
        print("❌ DEBUG: No se pudo convertir user_id a int")
        raise credentials_exception
    
    # Buscar usuario en BD
    user = db.query(User).filter(User.id == user_id).first()
    print(f"🔍 DEBUG: Usuario encontrado: {user.email if user else 'None'}")
    
    if user is None:
        print("❌ DEBUG: Usuario no existe en BD")
        raise credentials_exception
    
    if not user.is_active:
        print("❌ DEBUG: Usuario inactivo")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    print(f"✅ DEBUG: Usuario autenticado: {user.email}")
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    return current_user


def get_current_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de administrador"
        )
    return current_user


def get_current_superadmin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de super administrador"
        )
    return current_user


def check_user_country_access(
    user: User,
    country_id: int,
    db: Session
) -> bool:
    if user.role == UserRole.SUPERADMIN:
        return True
    
    user_country_ids = [country.id for country in user.countries]
    return country_id in user_country_ids


def get_user_countries(current_user: User = Depends(get_current_active_user)) -> list:
    if current_user.role == UserRole.SUPERADMIN:
        return None
    
    return [country.id for country in current_user.countries]