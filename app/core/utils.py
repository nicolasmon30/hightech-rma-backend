from datetime import datetime
from sqlalchemy.orm import Session
from app.models.rma import RMA, RMAStatus
from app.models.country import Country
from typing import Dict


# Traducciones de estados de RMA
RMA_STATUS_TRANSLATIONS: Dict[str, Dict[RMAStatus, str]] = {
    "es": {
        RMAStatus.RMA_SUBMITTED: "Solicitud Enviada",
        RMAStatus.AWAITING_GOODS: "Esperando Productos",
        RMAStatus.EVALUATING: "En Evaluación",
        RMAStatus.PROCESSING: "En Procesamiento",
        RMAStatus.PAYMENT: "Pago Pendiente",
        RMAStatus.IN_REPAIR: "En Reparación",
        RMAStatus.APPROVED: "Aprobado",
        RMAStatus.REJECTED: "Rechazado",
        RMAStatus.IN_SHIPPING: "En Envío",
        RMAStatus.COMPLETED: "Completado"
    },
    "en": {
        RMAStatus.RMA_SUBMITTED: "Request Submitted",
        RMAStatus.AWAITING_GOODS: "Awaiting Products",
        RMAStatus.EVALUATING: "Under Evaluation",
        RMAStatus.PROCESSING: "Processing",
        RMAStatus.PAYMENT: "Pending Payment",
        RMAStatus.IN_REPAIR: "Under Repair",
        RMAStatus.APPROVED: "Approved",
        RMAStatus.REJECTED: "Rejected",
        RMAStatus.IN_SHIPPING: "In Transit",
        RMAStatus.COMPLETED: "Completed"
    }
}


def get_rma_status_display(status: RMAStatus, language: str = "en") -> str:
    """
    Obtener el nombre traducido de un estado de RMA
    
    Args:
        status: Estado del RMA (enum)
        language: Código de idioma ('es' o 'en')
    
    Returns:
        Nombre del estado traducido
    """
    lang = language.lower() if language.lower() in ["es", "en"] else "en"
    return RMA_STATUS_TRANSLATIONS.get(lang, RMA_STATUS_TRANSLATIONS["en"]).get(status, status.value)


def generate_rma_number(db: Session, country_id: int) -> str:
    """
    Genera un número único de RMA
    
    Formato: RMA-{COUNTRY_CODE}-{YEAR}-{SEQUENCE}
    Ejemplo: RMA-US-2024-00001
    
    Args:
        db: Sesión de base de datos
        country_id: ID del país
    
    Returns:
        Número de RMA único
    """
    # Obtener código del país
    country = db.query(Country).filter(Country.id == country_id).first()
    if not country:
        raise ValueError("País no encontrado")
    
    country_code = country.code.upper()
    year = datetime.now().year
    
    # Obtener el último RMA del año para este país
    last_rma = (
        db.query(RMA)
        .filter(RMA.rma_number.like(f"RMA-{country_code}-{year}-%"))
        .order_by(RMA.rma_number.desc())
        .first()
    )
    
    if last_rma:
        # Extraer el número de secuencia
        try:
            last_sequence = int(last_rma.rma_number.split("-")[-1])
            new_sequence = last_sequence + 1
        except (ValueError, IndexError):
            new_sequence = 1
    else:
        new_sequence = 1
    
    # Formatear con ceros a la izquierda (5 dígitos)
    rma_number = f"RMA-{country_code}-{year}-{new_sequence:05d}"
    
    return rma_number