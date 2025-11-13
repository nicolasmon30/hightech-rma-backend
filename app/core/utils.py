from datetime import datetime
from sqlalchemy.orm import Session
from app.models.rma import RMA
from app.models.country import Country


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