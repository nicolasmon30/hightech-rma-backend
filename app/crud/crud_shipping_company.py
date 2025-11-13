from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.shipping_company import ShippingCompany
from app.models.country import Country
from app.schemas.shipping_company import ShippingCompanyCreate, ShippingCompanyUpdate


class CRUDShippingCompany(CRUDBase[ShippingCompany, ShippingCompanyCreate, ShippingCompanyUpdate]):
    """
    Operaciones CRUD para ShippingCompany
    """
    
    def create_with_countries(self, db: Session, *, obj_in: ShippingCompanyCreate) -> ShippingCompany:
        """
        Crear empresa transportadora con países asignados
        """
        db_obj = ShippingCompany(
            name=obj_in.name
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
        db_obj: ShippingCompany, 
        obj_in: ShippingCompanyUpdate
    ) -> ShippingCompany:
        """
        Actualizar empresa transportadora incluyendo países
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
    
    def get_by_country(self, db: Session, *, country_id: int) -> List[ShippingCompany]:
        """
        Obtener empresas transportadoras disponibles en un país
        """
        return (
            db.query(ShippingCompany)
            .join(ShippingCompany.countries)
            .filter(Country.id == country_id, ShippingCompany.is_active == True)
            .all()
        )
    
    def get_by_name(self, db: Session, *, name: str) -> Optional[ShippingCompany]:
        """
        Obtener empresa transportadora por nombre
        """
        return db.query(ShippingCompany).filter(ShippingCompany.name == name).first()


shipping_company = CRUDShippingCompany(ShippingCompany)
