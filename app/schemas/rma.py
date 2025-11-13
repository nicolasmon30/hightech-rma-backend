from pydantic import BaseModel, Field, ConfigDict, field_validator, computed_field
from typing import Optional, TYPE_CHECKING , List
from datetime import datetime
from app.models.rma import RMAStatus
from app.models.rma_item import ServiceType

# Imports condicionales para evitar referencias circulares
if TYPE_CHECKING:
    from app.schemas.brand import BrandResponse
    from app.schemas.product import ProductResponse
    from app.schemas.model import ModelResponse
    from app.schemas.country import CountryResponse
    from app.schemas.user import UserResponse

class RMAItemCreate(BaseModel):
    """Datos necesarios para crear un item de RMA"""
    brand_id: int = Field(..., gt=0, description="ID de la marca")
    product_id: int = Field(..., gt=0, description="ID del producto")
    model_id: int = Field(..., gt=0, description="ID del modelo")
    serial_number: str = Field(..., min_length=1, max_length=100, description="Número de serie único")
    service_type: ServiceType
    issue_description: str = Field(..., min_length=10, description="Descripción del problema")
    
    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra={
            "example": {
                "brand_id": 1,
                "product_id": 1,
                "model_id": 1,
                "serial_number": "SN123456789",
                "service_type": "warranty",
                "issue_description": "La pantalla no enciende después de caída"
            }
        }
    )


class RMAItemResponse(BaseModel):
    """Respuesta con información completa de un item"""
    id: int
    rma_id: int
    brand_id: int
    product_id: int
    model_id: int
    serial_number: str
    service_type: ServiceType 
    issue_description: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())
        
class RMABase(BaseModel):
    """Campos base de RMA"""
    company_name: str = Field(..., min_length=1, max_length=255)
    company_address: str = Field(..., min_length=1, max_length=500)
    postal_code: str = Field(..., min_length=1, max_length=20)


class RMACreate(RMABase):
    """Schema para crear RMA"""
    items: List[RMAItemCreate] = Field(..., min_length=1)
    
    @field_validator('items')
    @classmethod
    def validate_items(cls, v):
        """Validar que no haya seriales duplicados en el mismo RMA"""
        serials = [item.serial_number for item in v]
        if len(serials) != len(set(serials)):
            raise ValueError("No puedes tener números de serie duplicados en el mismo RMA")
        return v
    
    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra={
            "example": {
                "company_name": "Tech Solutions Inc",
                "company_address": "123 Main St, Miami, FL 33101",
                "postal_code": "33101",
                "items": [
                    {
                        "brand_id": 1,
                        "product_id": 1,
                        "model_id": 1,
                        "serial_number": "DELL-SN-001",
                        "service_type": "calibration",
                        "issue_description": "Pantalla rota después de caída"
                    },
                    {
                        "brand_id": 2,
                        "product_id": 3,
                        "model_id": 5,
                        "serial_number": "HP-SN-002",
                        "service_type": "repair",
                        "issue_description": "No enciende, LED parpadea"
                    }
                ]
            }
        }
    )


class RMAUpdate(BaseModel):
    """Schema para actualizar RMA"""
    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    company_address: Optional[str] = Field(None, min_length=1, max_length=500)
    postal_code: Optional[str] = Field(None, min_length=1, max_length=20)
    
    model_config = ConfigDict(protected_namespaces=())


class RMAResponse(RMABase):
    """Schema de respuesta de RMA"""
    id: int
    rma_number: Optional[str] = None  # Será None hasta que se apruebe
    status: RMAStatus
    country_id: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    # Datos de envío (opcionales)
    shipping_company: Optional[str] = None
    tracking_id: Optional[str] = None
    
    # Recordatorio de pago (opcional)
    last_payment_reminder: Optional[datetime] = None
    
    # Lista de items del RMA
    items: List[RMAItemResponse] = []
    
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class RMAStatusUpdate(BaseModel):
    """Schema para actualizar solo el estado del RMA"""
    new_status: RMAStatus
    comment: Optional[str] = Field(None, max_length=500)
    
    # Datos de envío (requeridos solo cuando new_status = IN_SHIPPING)
    shipping_company: Optional[str] = Field(None, max_length=255)
    tracking_id: Optional[str] = Field(None, max_length=255)
    
    model_config = ConfigDict(from_attributes=True)
    

class RMAListResponse(BaseModel):
    """Respuesta resumida para listados"""
    id: int
    rma_number: Optional[str] = None  # Será None hasta que se apruebe
    company_name: str
    status: RMAStatus
    created_at: datetime
    items_count: int = 0
    
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


# Schema con relaciones - Ya no es necesario porque RMAResponse contiene todo
# RMAWithRelations se puede eliminar si no se usa

# Resolver referencias circulares al final del archivo
from app.schemas.brand import BrandResponse
from app.schemas.product import ProductResponse
from app.schemas.model import ModelResponse
from app.schemas.country import CountryResponse
from app.schemas.user import UserResponse