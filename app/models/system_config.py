from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class SystemConfig(Base):
    """
    Configuración del sistema que puede ser modificada dinámicamente
    Solo puede ser modificada por SUPERADMIN
    """
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Clave de configuración (única)
    key = Column(String(100), unique=True, nullable=False, index=True)
    
    # Valor de la configuración
    value = Column(String(255), nullable=False)
    
    # Descripción de la configuración
    description = Column(String(500))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<SystemConfig(key='{self.key}', value='{self.value}')>"
