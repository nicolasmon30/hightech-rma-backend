from app.crud.base import CRUDBase
from app.models.country import Country
from app.schemas.country import CountryCreate, CountryUpdate
from sqlalchemy.orm import Session
from typing import Optional


class CRUDCountry(CRUDBase[Country, CountryCreate, CountryUpdate]):
    """
    Operaciones CRUD para Country
    """
    
    def get_by_code(self, db: Session, *, code: str) -> Optional[Country]:
        """
        Obtener país por código (US, CO)
        """
        return db.query(Country).filter(Country.code == code.upper()).first()
    
    def get_active(self, db: Session) -> list[Country]:
        """
        Obtener solo países activos
        """
        return db.query(Country).filter(Country.is_active == True).all()


country = CRUDCountry(Country)