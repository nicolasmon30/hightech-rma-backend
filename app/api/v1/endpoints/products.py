from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.api.deps import get_current_admin, get_current_active_user, get_current_superadmin
from app.crud import product as crud_product, brand as crud_brand
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductWithBrand
from app.models.user import User, UserRole

router = APIRouter()


@router.get("", response_model=List[ProductWithBrand])
def get_products(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)  # ✅ Todos los usuarios autenticados
) -> Any:
    """
    Obtener lista de productos (todos los roles)
    
    **Permisos:**
    - SUPERADMIN: Ve todos los productos
    - ADMIN: Ve productos de marcas disponibles en su(s) país(es)
    - USER: Ve productos de marcas disponibles en su(s) país(es)
    
    Los productos se obtienen a través de las marcas disponibles en los países
    del usuario.
    """
    if current_user.role == UserRole.SUPERADMIN:
        # SUPERADMIN ve todos los productos
        products = crud_product.get_multi(db, skip=skip, limit=limit)
    else:
        # ADMIN y USER ven productos de marcas de sus países
        products = []
        user_country_ids = [country.id for country in current_user.countries]
        
        # Obtener todas las marcas disponibles en los países del usuario
        all_brands = []
        for country_id in user_country_ids:
            brands = crud_brand.get_by_country(db, country_id=country_id)
            all_brands.extend(brands)
        
        # Eliminar marcas duplicadas
        unique_brands = {brand.id: brand for brand in all_brands}.values()
        
        # Obtener productos de esas marcas
        for brand in unique_brands:
            brand_products = crud_product.get_by_brand(db, brand_id=brand.id)
            products.extend(brand_products)
        
        # Eliminar productos duplicados y aplicar paginación manualmente
        unique_products = list({p.id: p for p in products}.values())
        products = unique_products[skip:skip + limit]
    
    return products


@router.get("/brand/{brand_id}", response_model=List[ProductResponse])
def get_products_by_brand(
    brand_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtener productos de una marca (público para formulario de RMA)
    """
    products = crud_product.get_by_brand(db, brand_id=brand_id)
    return products


@router.get("/{product_id}", response_model=ProductWithBrand)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # ✅ Todos los usuarios autenticados
) -> Any:
    """
    Obtener producto por ID (todos los roles)
    
    **Permisos:**
    - SUPERADMIN: Puede ver cualquier producto
    - ADMIN/USER: Solo puede ver productos de marcas disponibles en su(s) país(es)
    """
    product = crud_product.get(db, id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    # Verificar acceso (ADMIN/USER solo pueden ver productos de sus países)
    if current_user.role != UserRole.SUPERADMIN:
        # Verificar que la marca del producto esté en algún país del usuario
        product_brand_country_ids = [c.id for c in product.brand.countries]
        user_country_ids = [c.id for c in current_user.countries]
        
        has_access = any(c_id in user_country_ids for c_id in product_brand_country_ids)
        
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a este producto"
            )
    
    return product


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    *,
    db: Session = Depends(get_db),
    product_in: ProductCreate,
    current_user: User = Depends(get_current_superadmin)  # ✅ Solo SUPERADMIN
) -> Any:
    """
    Crear nuevo producto (solo SUPERADMIN)
    """
    # Verificar que la marca existe
    brand = crud_brand.get(db, id=product_in.brand_id)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marca no encontrada"
        )
    
    # Verificar si ya existe
    existing = crud_product.get_by_name_and_brand(
        db, 
        name=product_in.name, 
        brand_id=product_in.brand_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un producto con ese nombre para esta marca"
        )
    
    product = crud_product.create(db, obj_in=product_in)
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    product_in: ProductUpdate,
    current_user: User = Depends(get_current_superadmin)  # ✅ Solo SUPERADMIN
) -> Any:
    """
    Actualizar producto (solo SUPERADMIN)
    """
    product = crud_product.get(db, id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    product = crud_product.update(db, db_obj=product, obj_in=product_in)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    current_user: User = Depends(get_current_superadmin)  # ✅ Solo SUPERADMIN
) -> None:
    """
    Eliminar producto (solo SUPERADMIN)
    
    **Restricción:** No se puede eliminar un producto que esté siendo usado en
    modelos o RMAs existentes. En ese caso, desactiva el producto.
    """
    product = crud_product.get(db, id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    try:
        crud_product.delete(db, id=product_id)
    except IntegrityError as e:
        db.rollback()
        
        error_msg = str(e.orig)
        
        if "models" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": "No se puede eliminar el producto porque tiene modelos asociados",
                    "suggestion": "Desactiva el producto en lugar de eliminarlo o elimina primero los modelos asociados",
                    "code": "PRODUCT_HAS_MODELS"
                }
            )
        elif "rma_items" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": "No se puede eliminar el producto porque está siendo usado en RMAs existentes",
                    "suggestion": "Desactiva el producto en lugar de eliminarlo",
                    "code": "PRODUCT_HAS_RMA_ITEMS"
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": "No se puede eliminar el producto porque está siendo referenciado",
                    "suggestion": "Desactiva el producto en lugar de eliminarlo",
                    "code": "PRODUCT_IN_USE"
                }
            )