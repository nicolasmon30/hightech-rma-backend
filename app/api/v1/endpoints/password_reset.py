"""
Endpoints para recuperación de contraseña
"""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.crud import user as crud_user
from app.crud.crud_password_reset import password_reset_crud
from app.schemas.password_reset import (
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordResetResponse,
    PasswordResetConfirmResponse
)
from app.services.email_service import EmailService

router = APIRouter()


@router.post("/forgot-password", response_model=PasswordResetResponse)
def request_password_reset(
    *,
    db: Session = Depends(get_db),
    reset_request: PasswordResetRequest
) -> Any:
    """
    Solicitar recuperación de contraseña
    
    **Flujo:**
    1. Usuario ingresa su email
    2. Sistema verifica que el email existe
    3. Genera un token único de un solo uso (expira en 1 hora)
    4. Envía email con enlace de recuperación
    5. Usuario hace clic en el enlace y establece nueva contraseña
    
    **Seguridad:**
    - No revela si el email existe o no (previene enumeración)
    - Token de un solo uso
    - Expira en 1 hora
    - Invalida tokens anteriores
    """
    # Buscar usuario por email
    user = crud_user.get_by_email(db, email=reset_request.email)
    
    # Por seguridad, siempre retornar el mismo mensaje
    # (no revelar si el email existe o no)
    response_message = (
        "Si el email existe en nuestro sistema, recibirás instrucciones "
        "para recuperar tu contraseña en los próximos minutos."
    )
    
    if user and user.is_active:
        # Crear token de reset
        reset_token = password_reset_crud.create_reset_token(db, user_id=user.id)
        
        # Construir URL de reset (frontend)
        # En producción esto vendría de una variable de entorno
        frontend_url = settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else "http://localhost:3000"
        reset_url = f"{frontend_url}/reset-password"
        
        # Enviar email con token
        try:
            EmailService.send_password_reset_email(
                user_email=user.email,
                user_name=user.full_name,
                reset_token=reset_token.token,
                reset_url=reset_url,
                language=user.language.value
            )
            print(f"✅ Email de recuperación enviado a {user.email}")
        except Exception as e:
            print(f"❌ Error enviando email de recuperación: {str(e)}")
            # No fallar aquí, solo loguear
    else:
        # Usuario no existe o está inactivo
        # No hacer nada, pero tampoco revelar esta información
        print(f"⚠️ Intento de reset para email inexistente o inactivo: {reset_request.email}")
    
    return PasswordResetResponse(
        message=response_message,
        email=reset_request.email
    )


@router.post("/reset-password", response_model=PasswordResetConfirmResponse)
def confirm_password_reset(
    *,
    db: Session = Depends(get_db),
    reset_confirm: PasswordResetConfirm
) -> Any:
    """
    Confirmar reset de contraseña con token
    
    **Flujo:**
    1. Usuario hace clic en enlace del email
    2. Frontend muestra formulario para nueva contraseña
    3. Usuario ingresa nueva contraseña
    4. Sistema valida token
    5. Actualiza contraseña
    6. Marca token como usado
    
    **Validaciones:**
    - Token existe
    - Token no ha sido usado
    - Token no ha expirado
    - Usuario existe y está activo
    """
    # Validar token
    is_valid, error_message, user = password_reset_crud.validate_token(
        db, 
        token=reset_confirm.token
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    # Actualizar contraseña
    try:
        crud_user.update_password(
            db,
            user=user,
            new_password=reset_confirm.new_password
        )
        
        # Marcar token como usado
        password_reset_crud.mark_token_as_used(db, token=reset_confirm.token)
        
        print(f"✅ Contraseña actualizada exitosamente para {user.email}")
        
        return PasswordResetConfirmResponse(
            message="Contraseña actualizada exitosamente. Ahora puedes iniciar sesión con tu nueva contraseña.",
            success=True
        )
    
    except Exception as e:
        print(f"❌ Error actualizando contraseña: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar la contraseña. Intenta nuevamente."
        )


@router.post("/validate-reset-token")
def validate_reset_token(
    *,
    db: Session = Depends(get_db),
    token: str
) -> Any:
    """
    Validar si un token de reset es válido
    
    Útil para el frontend antes de mostrar el formulario de nueva contraseña
    """
    is_valid, error_message, user = password_reset_crud.validate_token(db, token=token)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    return {
        "valid": True,
        "message": "Token válido",
        "user_email": user.email
    }
