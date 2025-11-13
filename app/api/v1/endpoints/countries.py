from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_superadmin
from app.crud import country as crud_country
from app.schemas.country import CountryCreate, CountryUpdate, CountryResponse
from app.models.user import User

router = APIRouter()


@router.get("", response_model=List[CountryResponse])
def get_countries(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Obtener lista de países (público)
    """
    countries = crud_country.get_multi(db, skip=skip, limit=limit)
    return countries


@router.get("/active", response_model=List[CountryResponse])
def get_active_countries(
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtener solo países activos (público)
    """
    countries = crud_country.get_active(db)
    return countries


@router.get("/{country_id}", response_model=CountryResponse)
def get_country(
    country_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtener país por ID
    """
    country = crud_country.get(db, id=country_id)
    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="País no encontrado"
        )
    return country


@router.post("", response_model=CountryResponse, status_code=status.HTTP_201_CREATED)
def create_country(
    *,
    db: Session = Depends(get_db),
    country_in: CountryCreate,
    current_user: User = Depends(get_current_superadmin)
) -> Any:
    """
    Crear nuevo país (solo SUPERADMIN)
    """
    # Verificar si ya existe
    existing = crud_country.get_by_code(db, code=country_in.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un país con código {country_in.code}"
        )
    
    country = crud_country.create(db, obj_in=country_in)
    return country


@router.put("/{country_id}", response_model=CountryResponse)
def update_country(
    *,
    db: Session = Depends(get_db),
    country_id: int,
    country_in: CountryUpdate,
    current_user: User = Depends(get_current_superadmin)
) -> Any:
    """
    Actualizar país (solo SUPERADMIN)
    """
    country = crud_country.get(db, id=country_id)
    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="País no encontrado"
        )
    
    country = crud_country.update(db, db_obj=country, obj_in=country_in)
    return country


@router.delete("/{country_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_country(
    *,
    db: Session = Depends(get_db),
    country_id: int,
    current_user: User = Depends(get_current_superadmin)
) -> None:
    """
    Eliminar país (solo SUPERADMIN)
    """
    country = crud_country.get(db, id=country_id)
    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="País no encontrado"
        )
    
    crud_country.delete(db, id=country_id)