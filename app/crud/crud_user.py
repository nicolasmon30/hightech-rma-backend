from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.crud.base import CRUDBase
from app.models.user import User, UserRole
from app.models.country import Country
from app.models.password_reset import PasswordResetToken
from app.schemas.user import UserCreate, UserUpdate, UserCreateByAdmin, UserUpdateByAdmin
from app.core.security import get_password_hash, verify_password
from datetime import datetime


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """
    Operaciones CRUD para User
    """
    
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """
        Obtener usuario por email
        """
        return db.query(User).filter(User.email == email).first()
    
    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        Crear usuario normal (sin rol específico)
        """
        # Hashear contraseña
        hashed_password = get_password_hash(obj_in.password)
        
        # Crear usuario
        db_obj = User(
            email=obj_in.email,
            hashed_password=hashed_password,
            full_name=obj_in.full_name,
            phone=obj_in.phone,
            company=obj_in.company,
            language=obj_in.language,
            role=UserRole.USER  # Por defecto USER
        )
        
        # Asignar países
        if obj_in.country_ids:
            countries = db.query(Country).filter(Country.id.in_(obj_in.country_ids)).all()
            db_obj.countries = countries
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def create_by_admin(self, db: Session, *, obj_in: UserCreateByAdmin) -> User:
        """
        Crear usuario con rol específico (solo admins)
        """
        hashed_password = get_password_hash(obj_in.password)
        
        db_obj = User(
            email=obj_in.email,
            hashed_password=hashed_password,
            full_name=obj_in.full_name,
            phone=obj_in.phone,
            company=obj_in.company,
            language=obj_in.language,
            role=obj_in.role
        )
        
        if obj_in.country_ids:
            countries = db.query(Country).filter(Country.id.in_(obj_in.country_ids)).all()
            db_obj.countries = countries
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update_by_admin(self, db: Session, *, db_obj: User, obj_in: UserUpdateByAdmin) -> User:
        """
        Actualizar usuario por admin (puede cambiar rol, estado, países)
        """
        update_data = obj_in.model_dump(exclude_unset=True)
        
        # Manejar países si se incluyen en la actualización
        if "country_ids" in update_data:
            country_ids = update_data.pop("country_ids")
            if country_ids is not None:
                countries = db.query(Country).filter(Country.id.in_(country_ids)).all()
                db_obj.countries = countries
        
        # Actualizar el resto de campos
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        """
        Autenticar usuario (login)
        """
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        
        # Actualizar último login
        user.last_login = datetime.utcnow()
        db.commit()
        
        return user
    
    def update_password(self, db: Session, *, user: User, new_password: str) -> User:
        """
        Actualizar contraseña de usuario
        """
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        db.refresh(user)
        return user
    
    def deactivate(self, db: Session, *, user_id: int) -> User:
        """
        Desactivar usuario (soft delete)
        """
        user = self.get(db, id=user_id)
        if user:
            user.is_active = False
            db.commit()
            db.refresh(user)
        return user
    
    def activate(self, db: Session, *, user_id: int) -> User:
        """
        Activar usuario
        """
        user = self.get(db, id=user_id)
        if user:
            user.is_active = True
            db.commit()
            db.refresh(user)
        return user
    
    def get_by_country(self, db: Session, *, country_id: int) -> List[User]:
        """
        Obtener usuarios de un país específico
        """
        return db.query(User).join(User.countries).filter(Country.id == country_id).all()
    
    def get_multi_filtered(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None,
        country_id: Optional[int] = None,
        search: Optional[str] = None
    ) -> List[User]:
        """
        Obtener usuarios con filtros opcionales
        """
        query = db.query(User)
        
        # Filtrar por rol
        if role is not None:
            query = query.filter(User.role == role)
        
        # Filtrar por estado activo
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        # Filtrar por país
        if country_id is not None:
            query = query.join(User.countries).filter(Country.id == country_id)
        
        # Búsqueda por texto (email, nombre o empresa)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    User.email.ilike(search_term),
                    User.full_name.ilike(search_term),
                    User.company.ilike(search_term)
                )
            )
        
        return query.offset(skip).limit(limit).all()
    
    def is_active(self, user: User) -> bool:
        """
        Verificar si el usuario está activo
        """
        return user.is_active

    
    def delete(self, db: Session, *, id: int) -> Optional[User]:
        """
        Eliminar un usuario y sus tokens de reset de contraseña asociados
        """
        user = self.get(db, id=id)
        if user:
            # Primero eliminar todos los tokens de reset de contraseña del usuario
            db.query(PasswordResetToken).filter(
                PasswordResetToken.user_id == id
            ).delete(synchronize_session=False)
            
            # Luego eliminar el usuario
            db.delete(user)
            db.commit()
        return user

user = CRUDUser(User)