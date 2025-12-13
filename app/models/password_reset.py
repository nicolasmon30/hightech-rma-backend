"""
Modelo para tokens de recuperación de contraseña
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from app.core.database import Base


class PasswordResetToken(Base):
    """
    Tokens de un solo uso para recuperación de contraseña
    
    - El token expira en 1 hora
    - Solo puede usarse una vez
    - Se marca como usado después del reset
    """
    __tablename__ = "password_reset_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    
    # Relación con User
    user = relationship("User", backref="password_reset_tokens")
    
    def __repr__(self):
        return f"<PasswordResetToken(id={self.id}, user_id={self.user_id}, is_used={self.is_used})>"
    
    @property
    def is_expired(self) -> bool:
        """Verifica si el token ha expirado"""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        """Verifica si el token es válido (no usado y no expirado)"""
        return not self.is_used and not self.is_expired
    
    @classmethod
    def create_token_expiry(cls) -> datetime:
        """Crea una fecha de expiración de 1 hora desde ahora"""
        return datetime.utcnow() + timedelta(hours=1)
