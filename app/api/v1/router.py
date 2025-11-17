from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, 
    countries, 
    users, 
    brands, 
    products, 
    models, 
    rmas, 
    attachments, 
    password_reset,
    shipping_companies,
    websocket,
    public_tracking
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(password_reset.router, prefix="/auth", tags=["Password Reset"])
api_router.include_router(countries.router, prefix="/countries", tags=["Countries"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(brands.router, prefix="/brands", tags=["Brands"])
api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(models.router, prefix="/models", tags=["Models"])
api_router.include_router(shipping_companies.router, prefix="/shipping-companies", tags=["Shipping Companies"])
api_router.include_router(rmas.router, prefix="/rmas", tags=["RMAs"])
api_router.include_router(attachments.router, prefix="/rmas", tags=["RMA Attachments"])
api_router.include_router(websocket.router, tags=["WebSocket"]) 
api_router.include_router(public_tracking.router, prefix="/public", tags=["Public Tracking"])