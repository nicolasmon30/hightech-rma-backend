"""Schemas públicos para tracking de RMA por número.
Estos endpoints NO requieren autenticación y excluyen documentos adjuntos.
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime
from app.models.rma import RMAStatus
from app.models.rma_item import ServiceType
from app.core.utils import get_rma_status_display


class RMAPublicItem(BaseModel):
    """Item público de RMA con nombres de entidades."""
    id: int
    serial_number: str
    service_type: ServiceType
    issue_description: str
    brand_id: int
    brand_name: Optional[str] = None
    product_id: int
    product_name: Optional[str] = None
    model_id: int
    model_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class RMAPublicHistory(BaseModel):
    """Historial público simplificado (sin datos de usuario)."""
    previous_status: Optional[RMAStatus] = None
    new_status: RMAStatus
    changed_at: datetime
    comment: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class RMAPublicResponse(BaseModel):
    """Respuesta pública completa para tracking de RMA."""
    rma_number: str = Field(..., description="Número de RMA único")
    status: RMAStatus
    company_name: str
    company_address: str
    postal_code: str
    country_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Envío (solo si existe)
    shipping_company: Optional[str] = None
    tracking_id: Optional[str] = None

    # Items y historial
    items: List[RMAPublicItem]
    history: List[RMAPublicHistory]

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    @staticmethod
    def status_display_name(status: RMAStatus, language: str = "es") -> str:
        """
        Obtener el nombre traducido del estado
        
        Args:
            status: Estado del RMA
            language: Código de idioma ('es' o 'en'), por defecto 'es' para retrocompatibilidad
        
        Returns:
            Nombre del estado traducido
        """
        return get_rma_status_display(status, language)
