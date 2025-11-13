from app.core.database import Base
from app.models.country import Country
from app.models.user import User, UserRole, LanguageCode
from app.models.brand import Brand
from app.models.product import Product
from app.models.model import Model
from app.models.rma_item import ServiceType, RMAItem
from app.models.rma import RMA, RMAStatus
from app.models.rma_attachment import RMAAttachment, AttachmentType
from app.models.password_reset import PasswordResetToken
from app.models.shipping_company import ShippingCompany

# Esto asegura que SQLAlchemy conozca todos los modelos
__all__ = [
    "user_countries",
    "brand_countries",
    "shipping_company_countries",
    "Country",
    "User",
    "UserRole",
    "LanguageCode",
    "Brand",
    "Product",
    "Model",
    "RMA",
    "RMAStatus",
    "ServiceType",
    "RMAItem",
    "RMAAttachment",
    "AttachmentType",
    "PasswordResetToken",
    "ShippingCompany",
]