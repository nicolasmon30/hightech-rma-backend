# Schemas básicos primero
from app.schemas.country import CountryCreate, CountryUpdate, CountryResponse
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.brand import BrandCreate, BrandUpdate, BrandResponse
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.schemas.model import ModelCreate, ModelUpdate, ModelResponse
from app.schemas.shipping_company import (
    ShippingCompanyCreate,
    ShippingCompanyUpdate,
    ShippingCompanyResponse,
    ShippingCompanyWithCountries
)

# Schemas de RMA al final (dependen de los demás)
from app.schemas.rma import (
    RMACreate,
    RMAUpdate,
    RMAResponse,
    RMAStatusUpdate,
    RMAItemCreate,
    RMAItemResponse
)

# Schemas de adjuntos
from app.schemas.attachment import (
    AttachmentUpload,
    AttachmentResponse,
    AttachmentHistory,
    AttachmentListItem
)

# Schemas de configuración del sistema
from app.schemas.system_config import (
    SystemConfigCreate,
    SystemConfigUpdate,
    SystemConfigResponse,
    PaymentReminderConfigUpdate,
    PaymentReminderConfigResponse
)

__all__ = [
    # Countries
    "CountryCreate",
    "CountryUpdate",
    "CountryResponse",
    
    # Users
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    
    # Brands
    "BrandCreate",
    "BrandUpdate",
    "BrandResponse",
    
    # Products
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    
    # Models
    "ModelCreate",
    "ModelUpdate",
    "ModelResponse",
    
    # Shipping Companies
    "ShippingCompanyCreate",
    "ShippingCompanyUpdate",
    "ShippingCompanyResponse",
    "ShippingCompanyWithCountries",
    
    # RMAs
    "RMACreate",
    "RMAUpdate",
    "RMAResponse",
    "RMAStatusUpdate",
    "RMAItemCreate",
    "RMAItemResponse",
    
    # Attachments
    "AttachmentUpload",
    "AttachmentResponse",
    "AttachmentHistory",
    "AttachmentListItem",
    
    # System Config
    "SystemConfigCreate",
    "SystemConfigUpdate",
    "SystemConfigResponse",
    "PaymentReminderConfigUpdate",
    "PaymentReminderConfigResponse",
]