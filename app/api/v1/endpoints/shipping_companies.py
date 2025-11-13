from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.api.deps import get_current_active_user, get_current_superadmin
from app.crud import shipping_company as crud_shipping_company
from app.schemas.shipping_company import (
    ShippingCompanyCreate, 
    ShippingCompanyUpdate, 
    ShippingCompanyResponse,
    ShippingCompanyWithCountries
)
from app.models.user import User, UserRole

router = APIRouter()


@router.get("", response_model=List[ShippingCompanyWithCountries])
def get_shipping_companies(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)  # ✅ Todos los usuarios autenticados
) -> Any:
    """
    Listar empresas transportadoras (todos los roles)
    
    **Permisos:**
    - SUPERADMIN: Ve todas las empresas transportadoras
    - ADMIN: Ve empresas de su(s) país(es)
    - USER: Ve empresas de su(s) país(es)
    
    Los usuarios necesitan ver las empresas transportadoras para completar el campo shipping_company en RMAs.
    """
    if current_user.role == UserRole.SUPERADMIN:
        # SUPERADMIN ve todas
        companies = crud_shipping_company.get_multi(db, skip=skip, limit=limit)
    else:
        # ADMIN y USER ven empresas de sus países
        companies = []
        for country in current_user.countries:
            companies.extend(crud_shipping_company.get_by_country(db, country_id=country.id))
        
        # Eliminar duplicados
        companies = list({company.id: company for company in companies}.values())
    
    return companies


@router.get("/country/{country_id}", response_model=List[ShippingCompanyResponse])
def get_shipping_companies_by_country(
    country_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtener empresas transportadoras disponibles en un país
    """
    companies = crud_shipping_company.get_by_country(db, country_id=country_id)
    return companies


@router.get("/{company_id}", response_model=ShippingCompanyWithCountries)
def get_shipping_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Obtener empresa transportadora por ID (todos los roles)
    
    **Permisos:**
    - SUPERADMIN: Puede ver cualquier empresa
    - ADMIN/USER: Solo puede ver empresas de su(s) país(es)
    """
    company = crud_shipping_company.get(db, id=company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa transportadora no encontrada"
        )
    
    # Verificar acceso (ADMIN/USER solo pueden ver empresas de sus países)
    if current_user.role != UserRole.SUPERADMIN:
        company_country_ids = [c.id for c in company.countries]
        user_country_ids = [c.id for c in current_user.countries]
        
        if not any(c_id in user_country_ids for c_id in company_country_ids):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a esta empresa transportadora"
            )
    
    return company


@router.post("", response_model=ShippingCompanyResponse, status_code=status.HTTP_201_CREATED)
def create_shipping_company(
    *,
    db: Session = Depends(get_db),
    company_in: ShippingCompanyCreate,
    current_user: User = Depends(get_current_superadmin)  # ✅ Solo SUPERADMIN
) -> Any:
    """
    Crear nueva empresa transportadora (solo SUPERADMIN)
    """
    # Verificar si ya existe
    existing = crud_shipping_company.get_by_name(db, name=company_in.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una empresa transportadora con nombre {company_in.name}"
        )
    
    company = crud_shipping_company.create_with_countries(db, obj_in=company_in)
    return company


@router.put("/{company_id}", response_model=ShippingCompanyResponse)
def update_shipping_company(
    *,
    db: Session = Depends(get_db),
    company_id: int,
    company_in: ShippingCompanyUpdate,
    current_user: User = Depends(get_current_superadmin)  # ✅ Solo SUPERADMIN
) -> Any:
    """
    Actualizar empresa transportadora (solo SUPERADMIN)
    """
    company = crud_shipping_company.get(db, id=company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa transportadora no encontrada"
        )
    
    company = crud_shipping_company.update_with_countries(db, db_obj=company, obj_in=company_in)
    return company


@router.post("/{company_id}/deactivate", response_model=ShippingCompanyResponse)
def deactivate_shipping_company(
    *,
    db: Session = Depends(get_db),
    company_id: int,
    current_user: User = Depends(get_current_superadmin)  # ✅ Solo SUPERADMIN
) -> Any:
    """
    Desactivar empresa transportadora (solo SUPERADMIN)
    
    **Recomendado:** Usar esto en lugar de DELETE cuando la empresa tiene
    RMAs asociados. La empresa seguirá existiendo en RMAs históricos
    pero no estará disponible para nuevos RMAs.
    """
    company = crud_shipping_company.get(db, id=company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa transportadora no encontrada"
        )
    
    if not company.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La empresa ya está desactivada"
        )
    
    company_update = ShippingCompanyUpdate(is_active=False)
    company = crud_shipping_company.update(db, db_obj=company, obj_in=company_update)
    return company


@router.post("/{company_id}/activate", response_model=ShippingCompanyResponse)
def activate_shipping_company(
    *,
    db: Session = Depends(get_db),
    company_id: int,
    current_user: User = Depends(get_current_superadmin)  # ✅ Solo SUPERADMIN
) -> Any:
    """
    Activar empresa transportadora (solo SUPERADMIN)
    """
    company = crud_shipping_company.get(db, id=company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa transportadora no encontrada"
        )
    
    if company.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La empresa ya está activa"
        )
    
    company_update = ShippingCompanyUpdate(is_active=True)
    company = crud_shipping_company.update(db, db_obj=company, obj_in=company_update)
    return company


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shipping_company(
    *,
    db: Session = Depends(get_db),
    company_id: int,
    current_user: User = Depends(get_current_superadmin)  # ✅ Solo SUPERADMIN
) -> None:
    """
    Eliminar empresa transportadora (solo SUPERADMIN)
    
    **Restricción:** No se puede eliminar una empresa que esté siendo usada en RMAs existentes.
    
    En ese caso se debe desactivar la empresa en lugar de eliminarla.
    """
    company = crud_shipping_company.get(db, id=company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa transportadora no encontrada"
        )
    
    try:
        crud_shipping_company.delete(db, id=company_id)
    except IntegrityError as e:
        db.rollback()
        
        # Determinar qué está bloqueando la eliminación
        error_msg = str(e.orig)
        
        if "rma" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": "No se puede eliminar la empresa transportadora porque está siendo usada en RMAs existentes",
                    "suggestion": "Desactiva la empresa en lugar de eliminarla. Los RMAs históricos seguirán manteniendo esta información",
                    "code": "SHIPPING_COMPANY_HAS_RMAS"
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": "No se puede eliminar la empresa transportadora porque está siendo referenciada por otros registros",
                    "suggestion": "Desactiva la empresa en lugar de eliminarla",
                    "code": "SHIPPING_COMPANY_IN_USE"
                }
            )
