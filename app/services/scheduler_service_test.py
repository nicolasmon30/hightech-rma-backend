"""
⚠️ SCHEDULER PARA TESTING - SOLO DESARROLLO ⚠️
Este archivo configura el scheduler para pruebas RÁPIDAS con segundos
NO USAR EN PRODUCCIÓN

Para testing rápido:
- Intervalo de recordatorios: En SEGUNDOS (no días)
- Verificación del scheduler: Cada 3 SEGUNDOS

Uso: Modificar main.py temporalmente para importar este servicio
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
from app.services.email_service import EmailService

# Instancia global del scheduler
scheduler = BackgroundScheduler()
email_service = EmailService()

# ⚡ CONFIGURACIÓN DE TESTING (segundos en lugar de días/horas)
TEST_REMINDER_INTERVAL_SECONDS = 9  # Enviar recordatorio cada 9 segundos
TEST_CHECK_INTERVAL_SECONDS = 3     # Verificar cada 3 segundos


def check_and_send_payment_reminders():
    """
    Tarea programada que verifica RMAs en estado PAYMENT
    VERSIÓN TESTING: Usa SEGUNDOS en lugar de días
    """
    db: Session = SessionLocal()
    try:
        # Buscar todos los RMAs en estado PAYMENT
        rmas_pending_payment = db.query(RMA).filter(
            RMA.status == RMAStatus.PAYMENT
        ).all()
        
        now = datetime.utcnow()
        
        print(f"🔍 [TEST] Verificando recordatorios (cada {TEST_CHECK_INTERVAL_SECONDS}s, envío cada {TEST_REMINDER_INTERVAL_SECONDS}s)...")
        
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
            
            # ⚡ CAMBIO IMPORTANTE: Usar SEGUNDOS en lugar de días
            seconds_passed = (now - reference_date).total_seconds()
            
            print(f"   RMA {rma.rma_number or rma.id}: {int(seconds_passed)}s desde última verificación")
            
            if seconds_passed >= TEST_REMINDER_INTERVAL_SECONDS:
                # Enviar recordatorio
                user = db.query(User).filter(User.id == rma.created_by).first()
                if user:
                    try:
                        # Calcular "días" para mostrar en el email (simular)
                        simulated_days = int(seconds_passed / TEST_REMINDER_INTERVAL_SECONDS)
                        
                        email_service.send_payment_reminder_email(
                            user_email=user.email,
                            user_name=user.full_name,
                            rma_number=rma.rma_number or f"RMA #{rma.id}",
                            company_name=rma.company_name,
                            days_pending=simulated_days if simulated_days > 0 else 1
                        )
                        
                        # Actualizar fecha del último recordatorio
                        rma.last_payment_reminder = now
                        db.commit()
                        
                        print(f"✅ [TEST] Recordatorio enviado: RMA {rma.rma_number} ({int(seconds_passed)}s = {simulated_days} 'días' simulados)")
                    except Exception as e:
                        print(f"⚠️ Error enviando recordatorio para RMA {rma.id}: {e}")
                        db.rollback()
            else:
                wait_seconds = TEST_REMINDER_INTERVAL_SECONDS - int(seconds_passed)
                print(f"      └─> Esperando {wait_seconds}s más para próximo recordatorio")
    
    except Exception as e:
        print(f"❌ Error en tarea de recordatorios de pago: {e}")
    finally:
        db.close()


def start_scheduler():
    """
    Iniciar el scheduler de tareas en segundo plano
    VERSIÓN TESTING: Verifica cada 3 segundos
    """
    if not scheduler.running:
        # ⚡ PROGRAMAR TAREA CADA 3 SEGUNDOS (para testing)
        scheduler.add_job(
            check_and_send_payment_reminders,
            trigger=IntervalTrigger(seconds=TEST_CHECK_INTERVAL_SECONDS),
            id='payment_reminders_test',
            name='[TEST] Verificar y enviar recordatorios de pago',
            replace_existing=True,
            next_run_time=datetime.now()  # Ejecutar inmediatamente al iniciar
        )
        
        scheduler.start()
        print(f"⚡ [TESTING MODE] Scheduler iniciado:")
        print(f"   └─> Verificación cada: {TEST_CHECK_INTERVAL_SECONDS} SEGUNDOS")
        print(f"   └─> Recordatorio cada: {TEST_REMINDER_INTERVAL_SECONDS} SEGUNDOS")
        print(f"   ⚠️  NO USAR EN PRODUCCIÓN")


def stop_scheduler():
    """
    Detener el scheduler de tareas
    Se ejecuta al apagar la aplicación
    """
    if scheduler.running:
        scheduler.shutdown()
        print("🛑 [TEST] Scheduler de recordatorios detenido")


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
        print("⚡ [TEST] Verificación inmediata programada")
