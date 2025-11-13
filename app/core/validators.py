import re
from typing import Optional


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Valida la fortaleza de una contraseña
    
    Reglas:
    - Mínimo 8 caracteres
    - Al menos una mayúscula
    - Al menos una minúscula
    - Al menos un número
    
    Returns:
        (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    
    if not re.search(r"[A-Z]", password):
        return False, "La contraseña debe contener al menos una mayúscula"
    
    if not re.search(r"[a-z]", password):
        return False, "La contraseña debe contener al menos una minúscula"
    
    if not re.search(r"\d", password):
        return False, "La contraseña debe contener al menos un número"
    
    return True, None


def sanitize_string(text: str) -> str:
    """
    Sanitiza strings para prevenir inyecciones
    """
    if not text:
        return text
    
    # Remover espacios extras
    return text.strip()