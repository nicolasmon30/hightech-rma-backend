from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# Contexto para hashear contraseñas con bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con el hash
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Genera el hash de una contraseña
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT
    
    Args:
        data: Datos a codificar en el token (ej: {"sub": user_id})
        expires_delta: Tiempo de expiración personalizado
    
    Returns:
        Token JWT codificado
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow()  # Issued at
    })
    
    print(f"🔍 DEBUG CREATE TOKEN: Creando token con data: {to_encode}")  # DEBUG
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    print(f"🔍 DEBUG CREATE TOKEN: Token creado: {encoded_jwt[:50]}...")  # DEBUG
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodifica y valida un token JWT
    
    Args:
        token: Token JWT
    
    Returns:
        Payload del token o None si es inválido
    """
    try:
        print(f"🔍 DEBUG DECODE: Intentando decodificar token")  # DEBUG
        print(f"🔍 DEBUG DECODE: SECRET_KEY: {settings.SECRET_KEY[:10]}...")  # DEBUG
        print(f"🔍 DEBUG DECODE: ALGORITHM: {settings.ALGORITHM}")  # DEBUG
        
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        print(f"✅ DEBUG DECODE: Token decodificado exitosamente: {payload}")  # DEBUG
        return payload
        
    except JWTError as e:
        print(f"❌ DEBUG DECODE: Error JWTError: {str(e)}")  # DEBUG
        return None
    except Exception as e:
        print(f"❌ DEBUG DECODE: Error inesperado: {type(e).__name__} - {str(e)}")  # DEBUG
        return None