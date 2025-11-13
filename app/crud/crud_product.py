from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    """
    Operaciones CRUD para Product
    """
    
    def get_by_brand(self, db: Session, *, brand_id: int) -> List[Product]:
        """
        Obtener productos de una marca
        """
        return (
            db.query(Product)
            .filter(Product.brand_id == brand_id, Product.is_active == True)
            .all()
        )
    
    def get_by_name_and_brand(
        self, 
        db: Session, 
        *, 
        name: str, 
        brand_id: int
    ) -> Optional[Product]:
        """
        Obtener producto por nombre y marca
        """
        return (
            db.query(Product)
            .filter(Product.name == name, Product.brand_id == brand_id)
            .first()
        )


product = CRUDProduct(Product)