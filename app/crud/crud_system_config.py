from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.system_config import SystemConfig
from app.schemas.system_config import SystemConfigCreate, SystemConfigUpdate


class CRUDSystemConfig:
    """CRUD operations for SystemConfig"""
    
    def get(self, db: Session, config_id: int) -> Optional[SystemConfig]:
        """Obtener configuración por ID"""
        return db.query(SystemConfig).filter(SystemConfig.id == config_id).first()
    
    def get_by_key(self, db: Session, key: str) -> Optional[SystemConfig]:
        """Obtener configuración por clave"""
        return db.query(SystemConfig).filter(SystemConfig.key == key).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[SystemConfig]:
        """Obtener todas las configuraciones"""
        return db.query(SystemConfig).offset(skip).limit(limit).all()
    
    def create(self, db: Session, obj_in: SystemConfigCreate) -> SystemConfig:
        """Crear nueva configuración"""
        db_obj = SystemConfig(
            key=obj_in.key,
            value=obj_in.value,
            description=obj_in.description
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, db_obj: SystemConfig, obj_in: SystemConfigUpdate) -> SystemConfig:
        """Actualizar configuración existente"""
        db_obj.value = obj_in.value
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update_by_key(self, db: Session, key: str, value: str) -> Optional[SystemConfig]:
        """Actualizar configuración por clave"""
        db_obj = self.get_by_key(db, key)
        if db_obj:
            db_obj.value = value
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, config_id: int) -> Optional[SystemConfig]:
        """Eliminar configuración"""
        obj = db.query(SystemConfig).get(config_id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj
    
    def get_or_create(self, db: Session, key: str, default_value: str, description: str = None) -> SystemConfig:
        """Obtener configuración o crearla si no existe"""
        config = self.get_by_key(db, key)
        if not config:
            config = SystemConfig(
                key=key,
                value=default_value,
                description=description
            )
            db.add(config)
            db.commit()
            db.refresh(config)
        return config


system_config = CRUDSystemConfig()
