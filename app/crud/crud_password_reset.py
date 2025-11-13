"""
CRUD para tokens de recuperación de contraseña
"""
import secrets
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.password_reset import PasswordResetToken
from app.models.user import User


class CRUDPasswordReset:
    """
    Operaciones CRUD para tokens de recuperación de contraseña
    """
    
    @staticmethod
    def generate_reset_token() -> str:
        """
        Genera un token seguro y único
        Usa 32 bytes (256 bits) para máxima seguridad
        """
        return secrets.token_urlsafe(32)
    
    def create_reset_token(self, db: Session, *, user_id: int) -> PasswordResetToken:
        """
        Crea un token de reset para un usuario
        
        - Invalida todos los tokens anteriores del usuario
        - Genera un nuevo token que expira en 1 hora
        """
        # Invalidar tokens anteriores del usuario (por seguridad)
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.is_used == False
        ).update({"is_used": True, "used_at": datetime.utcnow()})
        
        # Crear nuevo token
        token = self.generate_reset_token()
        expires_at = PasswordResetToken.create_token_expiry()
        
        db_obj = PasswordResetToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        return db_obj
    
    def get_by_token(self, db: Session, *, token: str) -> Optional[PasswordResetToken]:
        """
        Obtiene un token de reset por su valor
        """
        return db.query(PasswordResetToken).filter(
            PasswordResetToken.token == token
        ).first()
    
    def validate_token(self, db: Session, *, token: str) -> tuple[bool, Optional[str], Optional[User]]:
        """
        Valida un token de reset
        
        Returns:
            tuple: (is_valid, error_message, user)
        """
        reset_token = self.get_by_token(db, token=token)
        
        if not reset_token:
            return False, "Token inválido", None
        
        if reset_token.is_used:
            return False, "Este token ya ha sido usado", None
        
        if reset_token.is_expired:
            return False, "El token ha expirado. Solicita uno nuevo", None
        
        # Token válido, obtener usuario
        user = db.query(User).filter(User.id == reset_token.user_id).first()
        
        if not user:
            return False, "Usuario no encontrado", None
        
        if not user.is_active:
            return False, "Usuario inactivo", None
        
        return True, None, user
    
    def mark_token_as_used(self, db: Session, *, token: str) -> bool:
        """
        Marca un token como usado
        """
        reset_token = self.get_by_token(db, token=token)
        if reset_token:
            reset_token.is_used = True
            reset_token.used_at = datetime.utcnow()
            db.commit()
            return True
        return False
    
    def cleanup_expired_tokens(self, db: Session) -> int:
        """
        Elimina tokens expirados (opcional, para limpieza de BD)
        Retorna el número de tokens eliminados
        """
        deleted = db.query(PasswordResetToken).filter(
            PasswordResetToken.expires_at < datetime.utcnow()
        ).delete()
        db.commit()
        return deleted


# Instancia global
password_reset_crud = CRUDPasswordReset()
