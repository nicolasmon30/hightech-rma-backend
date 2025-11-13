from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.brand import Brand
from app.models.country import Country
from app.schemas.brand import BrandCreate, BrandUpdate


class CRUDBrand(CRUDBase[Brand, BrandCreate, BrandUpdate]):
    """
    Operaciones CRUD para Brand
    """
    
    def create_with_countries(self, db: Session, *, obj_in: BrandCreate) -> Brand:
        """
        Crear marca con países asignados
        """
        db_obj = Brand(
            name=obj_in.name,
            description=obj_in.description
        )
        
        # Asignar países
        if obj_in.country_ids:
            countries = db.query(Country).filter(Country.id.in_(obj_in.country_ids)).all()
            db_obj.countries = countries
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update_with_countries(
        self, 
        db: Session, 
        *, 
        db_obj: Brand, 
        obj_in: BrandUpdate
    ) -> Brand:
        """
        Actualizar marca incluyendo países
        """
        update_data = obj_in.model_dump(exclude_unset=True, exclude={"country_ids"})
        
        # Actualizar campos básicos
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        # Actualizar países si se proporcionaron
        if obj_in.country_ids is not None:
            countries = db.query(Country).filter(Country.id.in_(obj_in.country_ids)).all()
            db_obj.countries = countries
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_country(self, db: Session, *, country_id: int) -> List[Brand]:
        """
        Obtener marcas disponibles en un país
        """
        return (
            db.query(Brand)
            .join(Brand.countries)
            .filter(Country.id == country_id, Brand.is_active == True)
            .all()
        )
    
    def get_by_name(self, db: Session, *, name: str) -> Optional[Brand]:
        """
        Obtener marca por nombre
        """
        return db.query(Brand).filter(Brand.name == name).first()


brand = CRUDBrand(Brand)