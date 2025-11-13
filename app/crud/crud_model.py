from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.model import Model
from app.schemas.model import ModelCreate, ModelUpdate


class CRUDModel(CRUDBase[Model, ModelCreate, ModelUpdate]):
    """
    Operaciones CRUD para Model
    """
    
    def get_by_product(self, db: Session, *, product_id: int) -> List[Model]:
        """
        Obtener modelos de un producto
        """
        return (
            db.query(Model)
            .filter(Model.product_id == product_id, Model.is_active == True)
            .all()
        )
    
    def get_by_name_and_product(
        self, 
        db: Session, 
        *, 
        name: str, 
        product_id: int
    ) -> Optional[Model]:
        """
        Obtener modelo por nombre y producto
        """
        return (
            db.query(Model)
            .filter(Model.name == name, Model.product_id == product_id)
            .first()
        )


model = CRUDModel(Model)