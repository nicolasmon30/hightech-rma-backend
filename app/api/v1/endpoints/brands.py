from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.api.deps import get_current_admin, get_current_active_user, get_current_superadmin
from app.crud import brand as crud_brand
from app.schemas.brand import BrandCreate, BrandUpdate, BrandResponse, BrandWithCountries
from app.models.user import User, UserRole

router = APIRouter()


@router.get("", response_model=List[BrandWithCountries])
def get_brands(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)  # ✅ Todos los usuarios autenticados
) -> Any:
    """
    Obtener lista de marcas (todos los roles)
    
    **Permisos:**
    - SUPERADMIN: Ve todas las marcas
    - ADMIN: Ve marcas de su(s) país(es)
    - USER: Ve marcas de su(s) país(es)
    
    Los usuarios necesitan ver las marcas para crear RMAs.
    """
    if current_user.role == UserRole.SUPERADMIN:
        # SUPERADMIN ve todas las marcas
        brands = crud_brand.get_multi(db, skip=skip, limit=limit)
    else:
        # ADMIN y USER ven marcas de sus países
        brands = []
        for country in current_user.countries:
            brands.extend(crud_brand.get_by_country(db, country_id=country.id))
        
        # Eliminar duplicados
        brands = list({brand.id: brand for brand in brands}.values())
    
    return brands


@router.get("/country/{country_id}", response_model=List[BrandResponse])
def get_brands_by_country(
    country_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtener marcas disponibles en un país (público para el formulario de RMA)
    """
    brands = crud_brand.get_by_country(db, country_id=country_id)
    return brands


@router.get("/{brand_id}", response_model=BrandWithCountries)
def get_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # ✅ Todos los usuarios autenticados
) -> Any:
    """
    Obtener marca por ID (todos los roles)
    
    **Permisos:**
    - SUPERADMIN: Puede ver cualquier marca
    - ADMIN/USER: Solo puede ver marcas de su(s) país(es)
    """
    brand = crud_brand.get(db, id=brand_id)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marca no encontrada"
        )
    
    # Verificar acceso (ADMIN/USER solo pueden ver marcas de sus países)
    if current_user.role != UserRole.SUPERADMIN:
        brand_country_ids = [c.id for c in brand.countries]
        user_country_ids = [c.id for c in current_user.countries]
        
        if not any(c_id in user_country_ids for c_id in brand_country_ids):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a esta marca"
            )
    
    return brand


@router.post("", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
def create_brand(
    *,
    db: Session = Depends(get_db),
    brand_in: BrandCreate,
    current_user: User = Depends(get_current_superadmin)  # ✅ Solo SUPERADMIN
) -> Any:
    """
    Crear nueva marca (solo SUPERADMIN)
    """
    # Verificar si ya existe
    existing = crud_brand.get_by_name(db, name=brand_in.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una marca con nombre {brand_in.name}"
        )
    
    brand = crud_brand.create_with_countries(db, obj_in=brand_in)
    return brand


@router.put("/{brand_id}", response_model=BrandResponse)
def update_brand(
    *,
    db: Session = Depends(get_db),
    brand_id: int,
    brand_in: BrandUpdate,
    current_user: User = Depends(get_current_superadmin)  # ✅ Solo SUPERADMIN
) -> Any:
    """
    Actualizar marca (solo SUPERADMIN)
    """
    brand = crud_brand.get(db, id=brand_id)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marca no encontrada"
        )
    
    brand = crud_brand.update_with_countries(db, db_obj=brand, obj_in=brand_in)
    return brand


@router.post("/{brand_id}/deactivate", response_model=BrandResponse)
def deactivate_brand(
    *,
    db: Session = Depends(get_db),
    brand_id: int,
    current_user: User = Depends(get_current_superadmin)  # ✅ Solo SUPERADMIN
) -> Any:
    """
    Desactivar marca (solo SUPERADMIN)
    
    **Recomendado:** Usar esto en lugar de DELETE cuando la marca tiene
    productos o RMAs asociados. La marca seguirá existiendo en RMAs históricos
    pero no estará disponible para nuevos RMAs.
    """
    brand = crud_brand.get(db, id=brand_id)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marca no encontrada"
        )
    
    if not brand.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La marca ya está desactivada"
        )
    
    brand_update = BrandUpdate(is_active=False)
    brand = crud_brand.update(db, db_obj=brand, obj_in=brand_update)
    return brand


@router.post("/{brand_id}/activate", response_model=BrandResponse)
def activate_brand(
    *,
    db: Session = Depends(get_db),
    brand_id: int,
    current_user: User = Depends(get_current_superadmin)  # ✅ Solo SUPERADMIN
) -> Any:
    """
    Activar marca (solo SUPERADMIN)
    """
    brand = crud_brand.get(db, id=brand_id)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marca no encontrada"
        )
    
    if brand.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La marca ya está activa"
        )
    
    brand_update = BrandUpdate(is_active=True)
    brand = crud_brand.update(db, db_obj=brand, obj_in=brand_update)
    return brand


@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_brand(
    *,
    db: Session = Depends(get_db),
    brand_id: int,
    current_user: User = Depends(get_current_superadmin)  # ✅ Solo SUPERADMIN
) -> None:
    """
    Eliminar marca (solo SUPERADMIN)
    
    **Restricción:** No se puede eliminar una marca que esté siendo usada por:
    - Productos existentes
    - RMA items existentes
    
    En ese caso se debe desactivar la marca en lugar de eliminarla.
    """
    brand = crud_brand.get(db, id=brand_id)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marca no encontrada"
        )
    
    try:
        crud_brand.delete(db, id=brand_id)
    except IntegrityError as e:
        db.rollback()
        
        # Determinar qué está bloqueando la eliminación
        error_msg = str(e.orig)
        
        if "products" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": "No se puede eliminar la marca porque tiene productos asociados",
                    "suggestion": "Desactiva la marca en lugar de eliminarla o elimina primero los productos asociados",
                    "code": "BRAND_HAS_PRODUCTS"
                }
            )
        elif "rma_items" in error_msg.lower() or "models" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": "No se puede eliminar la marca porque está siendo usada en RMAs existentes",
                    "suggestion": "Desactiva la marca en lugar de eliminarla. Los RMAs históricos seguirán manteniendo esta información",
                    "code": "BRAND_HAS_RMA_ITEMS"
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": "No se puede eliminar la marca porque está siendo referenciada por otros registros",
                    "suggestion": "Desactiva la marca en lugar de eliminarla",
                    "code": "BRAND_IN_USE"
                }
            )