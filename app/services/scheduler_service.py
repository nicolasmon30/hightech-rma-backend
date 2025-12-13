"""
Servicio de programación de tareas automáticas
Gestiona recordatorios de pago para RMAs en estado PAYMENT
Configuración flexible a través de variables de entorno y base de datos
"""
from datetime import datetime, timedelta
from typing import Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.config import settings
from app.models.rma import RMA, RMAStatus
from app.models.user import User
from app.models.system_config import SystemConfig
from app.services.email_service import EmailService

# Instancia global del scheduler
scheduler = BackgroundScheduler()
email_service = EmailService()


def get_config_value(db: Session, key: str, default_value: int) -> int:
    """
    Obtiene un valor de configuración desde la BD o usa el valor por defecto
    """
    try:
        config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
        if config:
            return int(config.value)
    except Exception as e:
        print(f"⚠️ Error obteniendo configuración {key}: {e}")
    
    return default_value


def check_and_send_payment_reminders():
    """
    Tarea programada que verifica RMAs en estado PAYMENT
    y envía recordatorios según el intervalo configurado
    
    Configuración:
    - PAYMENT_REMINDER_INTERVAL_DAYS: Días entre recordatorios (desde BD o default: 3)
    """
    db: Session = SessionLocal()
    try:
        # Obtener intervalo configurado desde BD o usar default
        reminder_interval_days = get_config_value(
            db, 
            "PAYMENT_REMINDER_INTERVAL_DAYS", 
            settings.PAYMENT_REMINDER_INTERVAL_DAYS
        )
        
        # Buscar todos los RMAs en estado PAYMENT
        rmas_pending_payment = db.query(RMA).filter(
            RMA.status == RMAStatus.PAYMENT
        ).all()
        
        now = datetime.utcnow()
        
        print(f"🔍 Verificando recordatorios de pago (intervalo: {reminder_interval_days} días)...")
        
        for rma in rmas_pending_payment:
            # Si nunca se ha enviado recordatorio, usar la fecha del último cambio de estado
            last_reminder = rma.last_payment_reminder
            
            if last_reminder is None:
                # Buscar cuándo entró al estado PAYMENT
                from app.models.rma import RMAHistory
                last_history = db.query(RMAHistory).filter(
                    RMAHistory.rma_id == rma.id,
                    RMAHistory.new_status == RMAStatus.PAYMENT
                ).order_by(RMAHistory.changed_at.desc()).first()
                
                if last_history:
                    reference_date = last_history.changed_at
                else:
                    reference_date = rma.updated_at
            else:
                reference_date = last_reminder
            
            # Verificar si han pasado los días configurados
            days_passed = (now - reference_date).days
            
            if days_passed >= reminder_interval_days:
                # Enviar recordatorio
                user = db.query(User).filter(User.id == rma.created_by).first()
                if user:
                    try:
                        email_service.send_payment_reminder_email(
                            user_email=user.email,
                            user_name=user.full_name,
                            rma_number=rma.rma_number or f"RMA #{rma.id}",
                            company_name=rma.company_name,
                            days_pending=days_passed
                        )
                        
                        # Actualizar fecha del último recordatorio
                        rma.last_payment_reminder = now
                        db.commit()
                        
                        print(f"✅ Recordatorio enviado: RMA {rma.rma_number} ({days_passed} días pendientes)")
                    except Exception as e:
                        print(f"⚠️ Error enviando recordatorio para RMA {rma.id}: {e}")
                        db.rollback()
    
    except Exception as e:
        print(f"❌ Error en tarea de recordatorios de pago: {e}")
    finally:
        db.close()


def start_scheduler():
    """
    Iniciar el scheduler de tareas en segundo plano
    Se ejecuta al iniciar la aplicación
    
    Configuración:
    - PAYMENT_REMINDER_CHECK_INTERVAL_HOURS: Frecuencia de verificación (desde BD o default: 24)
    
    Nota: Los cambios de configuración se aplicarán en el próximo reinicio del scheduler
    """
    if not scheduler.running:
        db = SessionLocal()
        try:
            # Obtener intervalo configurado desde BD o usar default
            check_interval_hours = get_config_value(
                db,
                "PAYMENT_REMINDER_CHECK_INTERVAL_HOURS",
                settings.PAYMENT_REMINDER_CHECK_INTERVAL_HOURS
            )
        finally:
            db.close()
        
        # Programar tarea según configuración
        scheduler.add_job(
            check_and_send_payment_reminders,
            trigger=IntervalTrigger(hours=check_interval_hours),
            id='payment_reminders',
            name='Verificar y enviar recordatorios de pago',
            replace_existing=True,
            next_run_time=datetime.now()  # Ejecutar inmediatamente al iniciar
        )
        
        scheduler.start()
        print(f"🕐 Scheduler iniciado: recordatorios cada {check_interval_hours}h")


def restart_scheduler():
    """
    Reconfigurar el scheduler para aplicar nuevas configuraciones
    Debe ser llamado después de actualizar configuraciones en BD
    
    En lugar de reiniciar completamente, solo reconfigura el job existente
    """
    if not scheduler.running:
        print("⚠️ Scheduler no está corriendo, iniciando...")
        start_scheduler()
        return
    
    print("🔄 Reconfigurando scheduler con nueva configuración...")
    
    db = SessionLocal()
    try:
        # Obtener nueva configuración desde BD
        check_interval_hours = get_config_value(
            db,
            "PAYMENT_REMINDER_CHECK_INTERVAL_HOURS",
            settings.PAYMENT_REMINDER_CHECK_INTERVAL_HOURS
        )
    finally:
        db.close()
    
    # Reconfigurar el job existente con el nuevo intervalo
    scheduler.reschedule_job(
        'payment_reminders',
        trigger=IntervalTrigger(hours=check_interval_hours)
    )
    
    print(f"✅ Scheduler reconfigurado: recordatorios cada {check_interval_hours}h")


def stop_scheduler():
    """
    Detener el scheduler de tareas
    Se ejecuta al apagar la aplicación
    """
    if scheduler.running:
        scheduler.shutdown()
        print("🛑 Scheduler de recordatorios de pago detenido")


def schedule_immediate_check():
    """
    Programar una verificación inmediata (útil para testing o forzar revisión)
    """
    if scheduler.running:
        scheduler.add_job(
            check_and_send_payment_reminders,
            id='immediate_check',
            replace_existing=True
        )
        print("⚡ Verificación inmediata de recordatorios programada")
