from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum, Table, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base
from app.models.associations import user_countries  # Importar tabla intermedia


class UserRole(str, enum.Enum):
    """Roles de usuario"""
    USER = "user"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"


class LanguageCode(str, enum.Enum):
    """Idiomas soportados"""
    EN = "en"
    ES = "es"


class User(Base):
    """
    Usuarios del sistema (clientes, admins, superadmins)
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Autenticación
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Información personal
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50))
    company = Column(String(255))
    
    # Configuración
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    language = Column(SQLEnum(LanguageCode), default=LanguageCode.EN)
    
    # Estado
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relaciones
    countries = relationship("Country", secondary=user_countries, back_populates="users")
    # rmas = relationship("RMA", back_populates="creator", foreign_keys="RMA.created_by")
    
    def __repr__(self):
        return f"<User {self.email} ({self.role})>"