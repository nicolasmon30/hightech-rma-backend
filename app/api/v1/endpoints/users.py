from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import (
    get_current_active_user, 
    get_current_admin, 
    get_current_superadmin
)
from app.crud import user as crud_user
from app.schemas.user import (
    UserResponse, 
    UserWithCountries, 
    UserCreateByAdmin, 
    UserUpdateByAdmin,
    UserUpdate,
    UserPasswordReset
)
from app.models.user import User, UserRole
from app.services.email_service import EmailService

router = APIRouter()


@router.get("/me", response_model=UserWithCountries)
def get_current_user_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Obtener información del usuario actual (todos los roles)
    """
    # Eager loading de countries para evitar lazy loading issues
    from sqlalchemy.orm import joinedload
    
    user = db.query(User).options(
        joinedload(User.countries)
    ).filter(User.id == current_user.id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return user
    print(f"🔍 Usuario solicitado: {current_user.email}")
    print(f"🔍 Países: {[c.name for c in current_user.countries]}")
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Actualizar información del usuario actual (todos los roles)
    """
    user = crud_user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("", response_model=List[UserWithCountries])
def get_users(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=500, description="Número máximo de registros"),
    role: UserRole | None = Query(None, description="Filtrar por rol"),
    is_active: bool | None = Query(None, description="Filtrar por estado activo"),
    country_id: int | None = Query(None, description="Filtrar por país"),
    search: str | None = Query(None, description="Buscar por email, nombre o empresa"),
    current_user: User = Depends(get_current_admin)
) -> Any:
    """
    Obtener lista de usuarios con filtros opcionales
    - **ADMIN**: Ve solo usuarios de sus países
    - **SUPERADMIN**: Ve todos los usuarios
    """
    # Si es SUPERADMIN, puede ver todos con filtros
    if current_user.role == UserRole.SUPERADMIN:
        users = crud_user.get_multi_filtered(
            db,
            skip=skip,
            limit=limit,
            role=role,
            is_active=is_active,
            country_id=country_id,
            search=search
        )
    else:
        # Admin solo ve usuarios de sus países
        admin_country_ids = [c.id for c in current_user.countries]
        users = []
        
        # Si hay filtro de país, verificar que el admin tenga acceso
        if country_id is not None:
            if country_id not in admin_country_ids:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tienes acceso a usuarios de ese país"
                )
            # Obtener usuarios de ese país con filtros
            users = crud_user.get_multi_filtered(
                db,
                skip=skip,
                limit=limit,
                role=role,
                is_active=is_active,
                country_id=country_id,
                search=search
            )
        else:
            # Obtener usuarios de todos los países del admin
            for cid in admin_country_ids:
                country_users = crud_user.get_multi_filtered(
                    db,
                    skip=0,  # No aplicar skip por país
                    limit=limit,
                    role=role,
                    is_active=is_active,
                    country_id=cid,
                    search=search
                )
                users.extend(country_users)
            
            # Aplicar skip y limit al resultado combinado
            users = users[skip:skip + limit]
    
    return users


@router.get("/{user_id}", response_model=UserWithCountries)
def get_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user: User = Depends(get_current_admin)
) -> Any:
    """
    Obtener usuario por ID
    - **ADMIN**: Solo puede ver usuarios de sus países
    - **SUPERADMIN**: Puede ver cualquier usuario
    """
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Verificar permisos (admin solo ve usuarios de su país)
    if current_user.role != UserRole.SUPERADMIN:
        user_country_ids = [c.id for c in user.countries]
        admin_country_ids = [c.id for c in current_user.countries]
        
        if not any(c_id in admin_country_ids for c_id in user_country_ids):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a este usuario"
            )
    
    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreateByAdmin,
    current_user: User = Depends(get_current_superadmin)
) -> Any:
    """
    Crear nuevo usuario (solo SUPERADMIN)
    
    Envía automáticamente un email de bienvenida con la contraseña temporal
    """
    # Verificar si el email ya existe
    existing_user = crud_user.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Guardar la contraseña antes de hashearla para enviarla por email
    temp_password = user_in.password
    
    # Crear usuario
    user = crud_user.create_by_admin(db, obj_in=user_in)
    
    # Enviar email de bienvenida con contraseña temporal
    try:
        EmailService.send_admin_welcome_email(
            user_email=user.email,
            user_name=user.full_name,
            user_role=user.role.value,
            temp_password=temp_password,
            language=user.language.value
        )
    except Exception as e:
        # No fallar si el email no se puede enviar
        print(f"⚠️ No se pudo enviar email de bienvenida: {str(e)}")
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    user_in: UserUpdateByAdmin,
    current_user: User = Depends(get_current_superadmin)
) -> Any:
    """
    Actualizar usuario (solo SUPERADMIN)
    
    Puede actualizar: datos personales, rol, estado activo, países asignados
    """
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # No puede cambiar su propio rol
    if user.id == current_user.id and user_in.role is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes cambiar tu propio rol"
        )
    
    user = crud_user.update_by_admin(db, db_obj=user, obj_in=user_in)
    return user


@router.post("/{user_id}/reset-password", response_model=UserResponse)
def reset_user_password(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    password_in: UserPasswordReset,
    current_user: User = Depends(get_current_superadmin)
) -> Any:
    """
    Resetear contraseña de usuario (solo SUPERADMIN)
    """
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    user = crud_user.update_password(db, user=user, new_password=password_in.new_password)
    return user


@router.post("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user: User = Depends(get_current_superadmin)
) -> Any:
    """
    Desactivar usuario (soft delete) - Solo SUPERADMIN
    
    El usuario no podrá hacer login pero sus datos se mantienen
    """
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # No puede desactivarse a sí mismo
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes desactivarte a ti mismo"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya está desactivado"
        )
    
    user = crud_user.deactivate(db, user_id=user_id)
    return user


@router.post("/{user_id}/activate", response_model=UserResponse)
def activate_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user: User = Depends(get_current_superadmin)
) -> Any:
    """
    Activar usuario - Solo SUPERADMIN
    """
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya está activo"
        )
    
    user = crud_user.activate(db, user_id=user_id)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user: User = Depends(get_current_superadmin)
) -> None:
    """
    Eliminar usuario permanentemente (hard delete) - Solo SUPERADMIN
    
    ⚠️ CUIDADO: Esta acción es irreversible
    
    Se recomienda usar deactivate en lugar de delete
    """
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # No puede eliminarse a sí mismo
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminarte a ti mismo"
        )
    
    crud_user.delete(db, id=user_id)