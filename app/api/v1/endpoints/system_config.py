from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db, get_current_superadmin
from app.models.user import User
from app.crud.crud_system_config import system_config
from app.schemas.system_config import (
    SystemConfigResponse,
    SystemConfigCreate,
    SystemConfigUpdate,
    PaymentReminderConfigUpdate,
    PaymentReminderConfigResponse
)
from app.core.config import settings
from app.services import scheduler_service

router = APIRouter()


@router.get("/payment-reminders", response_model=PaymentReminderConfigResponse)
def get_payment_reminder_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superadmin)
):
    """
    Obtener configuración actual de recordatorios de pago (solo SUPERADMIN)
    """
    # Obtener configuraciones desde BD o usar valores por defecto
    interval_config = system_config.get_or_create(
        db,
        key="PAYMENT_REMINDER_INTERVAL_DAYS",
        default_value=str(settings.PAYMENT_REMINDER_INTERVAL_DAYS),
        description="Días entre envío de recordatorios de pago"
    )
    
    check_config = system_config.get_or_create(
        db,
        key="PAYMENT_REMINDER_CHECK_INTERVAL_HOURS",
        default_value=str(settings.PAYMENT_REMINDER_CHECK_INTERVAL_HOURS),
        description="Frecuencia de verificación del scheduler en horas"
    )
    
    return PaymentReminderConfigResponse(
        payment_reminder_interval_days=int(interval_config.value),
        payment_reminder_check_interval_hours=int(check_config.value)
    )


@router.put("/payment-reminders", response_model=PaymentReminderConfigResponse)
def update_payment_reminder_config(
    config_update: PaymentReminderConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superadmin)
):
    """
    Actualizar configuración de recordatorios de pago (solo SUPERADMIN)
    
    Parámetros:
    - payment_reminder_interval_days: Días entre recordatorios (1-30)
    - payment_reminder_check_interval_hours: Frecuencia de verificación en horas (1-168)
    
    Nota: El scheduler se reiniciará automáticamente para aplicar los cambios
    """
    print(f"📝 PUT recibido - Días: {config_update.payment_reminder_interval_days}, Horas: {config_update.payment_reminder_check_interval_hours}")
    
    # Actualizar intervalo de días
    interval_config = system_config.update_by_key(
        db,
        key="PAYMENT_REMINDER_INTERVAL_DAYS",
        value=str(config_update.payment_reminder_interval_days)
    )
    
    if not interval_config:
        interval_config = system_config.create(
            db,
            SystemConfigCreate(
                key="PAYMENT_REMINDER_INTERVAL_DAYS",
                value=str(config_update.payment_reminder_interval_days),
                description="Días entre envío de recordatorios de pago"
            )
        )
    
    # Actualizar frecuencia de verificación
    check_config = system_config.update_by_key(
        db,
        key="PAYMENT_REMINDER_CHECK_INTERVAL_HOURS",
        value=str(config_update.payment_reminder_check_interval_hours)
    )
    
    if not check_config:
        check_config = system_config.create(
            db,
            SystemConfigCreate(
                key="PAYMENT_REMINDER_CHECK_INTERVAL_HOURS",
                value=str(config_update.payment_reminder_check_interval_hours),
                description="Frecuencia de verificación del scheduler en horas"
            )
        )
    
    print(f"💾 Configuración guardada en BD")
    
    # Reconfigurar scheduler para aplicar cambios inmediatamente
    try:
        print(f"🔧 Llamando a restart_scheduler()...")
        scheduler_service.restart_scheduler()
        print(f"✅ Configuración actualizada - Días: {config_update.payment_reminder_interval_days}, Horas: {config_update.payment_reminder_check_interval_hours}")
    except Exception as e:
        print(f"⚠️ Error reconfigurando scheduler: {e}")
        import traceback
        traceback.print_exc()
        # No fallar la petición si el scheduler tiene problemas
        # Los nuevos valores se aplicarán en el próximo reinicio del servidor
    
    return PaymentReminderConfigResponse(
        payment_reminder_interval_days=int(interval_config.value),
        payment_reminder_check_interval_hours=int(check_config.value)
    )


@router.get("/", response_model=List[SystemConfigResponse])
def get_all_configs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superadmin)
):
    """
    Obtener todas las configuraciones del sistema (solo SUPERADMIN)
    """
    configs = system_config.get_multi(db, skip=skip, limit=limit)
    return configs


@router.get("/{key}", response_model=SystemConfigResponse)
def get_config_by_key(
    key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superadmin)
):
    """
    Obtener una configuración específica por clave (solo SUPERADMIN)
    """
    config = system_config.get_by_key(db, key=key)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuración con clave '{key}' no encontrada"
        )
    return config


@router.post("/", response_model=SystemConfigResponse, status_code=status.HTTP_201_CREATED)
def create_config(
    config_in: SystemConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superadmin)
):
    """
    Crear nueva configuración del sistema (solo SUPERADMIN)
    """
    # Verificar que la clave no exista
    existing = system_config.get_by_key(db, key=config_in.key)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una configuración con la clave '{config_in.key}'"
        )
    
    return system_config.create(db, obj_in=config_in)


@router.put("/{key}", response_model=SystemConfigResponse)
def update_config(
    key: str,
    config_update: SystemConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superadmin)
):
    """
    Actualizar configuración existente (solo SUPERADMIN)
    """
    config = system_config.get_by_key(db, key=key)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuración con clave '{key}' no encontrada"
        )
    
    return system_config.update(db, db_obj=config, obj_in=config_update)


@router.delete("/{key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_config(
    key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superadmin)
):
    """
    Eliminar configuración (solo SUPERADMIN)
    
    Precaución: No eliminar configuraciones críticas del sistema
    """
    config = system_config.get_by_key(db, key=key)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuración con clave '{key}' no encontrada"
        )
    
    system_config.delete(db, config_id=config.id)
    return None
