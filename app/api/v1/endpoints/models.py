from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.api.deps import get_current_admin, get_current_active_user, get_current_superadmin
from app.crud import model as crud_model, product as crud_product, brand as crud_brand
from app.schemas.model import ModelCreate, ModelUpdate, ModelResponse, ModelWithProduct
from app.models.user import User, UserRole

router = APIRouter()


@router.get("", response_model=List[ModelWithProduct])
def get_models(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)  # ✅ Todos los usuarios autenticados
) -> Any:
    """
    Obtener lista de modelos (todos los roles)
    
    **Permisos:**
    - SUPERADMIN: Ve todos los modelos
    - ADMIN: Ve modelos de productos cuyas marcas están en su(s) país(es)
    - USER: Ve modelos de productos cuyas marcas están en su(s) país(es)
    """
    if current_user.role == UserRole.SUPERADMIN:
        # SUPERADMIN ve todos los modelos
        models = crud_model.get_multi(db, skip=skip, limit=limit)
    else:
        # ADMIN y USER ven modelos de productos de marcas de sus países
        models = []
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
            
            # Obtener modelos de cada producto
            for product in brand_products:
                product_models = crud_model.get_by_product(db, product_id=product.id)
                models.extend(product_models)
        
        # Eliminar modelos duplicados y aplicar paginación manualmente
        unique_models = list({m.id: m for m in models}.values())
        models = unique_models[skip:skip + limit]
    
    return models


@router.get("/product/{product_id}", response_model=List[ModelResponse])
def get_models_by_product(
    product_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtener modelos de un producto (público para formulario de RMA)
    """
    models = crud_model.get_by_product(db, product_id=product_id)
    return models


@router.get("/{model_id}", response_model=ModelWithProduct)
def get_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # ✅ Todos los usuarios autenticados
) -> Any:
    """
    Obtener modelo por ID (todos los roles)
    
    **Permisos:**
    - SUPERADMIN: Puede ver cualquier modelo
    - ADMIN/USER: Solo puede ver modelos de productos cuyas marcas estén en su(s) país(es)
    """
    model = crud_model.get(db, id=model_id)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Modelo no encontrado"
        )
    
    # Verificar acceso (ADMIN/USER solo pueden ver modelos de sus países)
    if current_user.role != UserRole.SUPERADMIN:
        # Verificar que la marca del producto esté en algún país del usuario
        model_brand_country_ids = [c.id for c in model.product.brand.countries]
        user_country_ids = [c.id for c in current_user.countries]
        
        has_access = any(c_id in user_country_ids for c_id in model_brand_country_ids)
        
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a este modelo"
            )
    
    return model


@router.post("", response_model=ModelResponse, status_code=status.HTTP_201_CREATED)
def create_model(
    *,
    db: Session = Depends(get_db),
    model_in: ModelCreate,
    current_user: User = Depends(get_current_superadmin)  # ✅ Solo SUPERADMIN
) -> Any:
    """
    Crear nuevo modelo (solo SUPERADMIN)
    """
    # Verificar que el producto existe
    product = crud_product.get(db, id=model_in.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    # Verificar si ya existe
    existing = crud_model.get_by_name_and_product(
        db,
        name=model_in.name,
        product_id=model_in.product_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un modelo con ese nombre para este producto"
        )
    
    model = crud_model.create(db, obj_in=model_in)
    return model


@router.put("/{model_id}", response_model=ModelResponse)
def update_model(
    *,
    db: Session = Depends(get_db),
    model_id: int,
    model_in: ModelUpdate,
    current_user: User = Depends(get_current_superadmin)  # ✅ Solo SUPERADMIN
) -> Any:
    """
    Actualizar modelo (solo SUPERADMIN)
    """
    model = crud_model.get(db, id=model_id)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Modelo no encontrado"
        )
    
    model = crud_model.update(db, db_obj=model, obj_in=model_in)
    return model


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_model(
    *,
    db: Session = Depends(get_db),
    model_id: int,
    current_user: User = Depends(get_current_superadmin)  # ✅ Solo SUPERADMIN
) -> None:
    """
    Eliminar modelo (solo SUPERADMIN)
    
    **Restricción:** No se puede eliminar un modelo que esté siendo usado en
    RMA items existentes. En ese caso, desactiva el modelo.
    """
    model = crud_model.get(db, id=model_id)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Modelo no encontrado"
        )
    
    try:
        crud_model.delete(db, id=model_id)
    except IntegrityError as e:
        db.rollback()
        
        error_msg = str(e.orig)
        
        if "rma_items" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": "No se puede eliminar el modelo porque está siendo usado en RMAs existentes",
                    "suggestion": "Desactiva el modelo en lugar de eliminarlo. Los RMAs históricos seguirán manteniendo esta información",
                    "code": "MODEL_HAS_RMA_ITEMS"
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": "No se puede eliminar el modelo porque está siendo referenciado",
                    "suggestion": "Desactiva el modelo en lugar de eliminarlo",
                    "code": "MODEL_IN_USE"
                }
            )