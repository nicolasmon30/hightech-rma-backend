"""
Script para verificar y probar la configuración de recordatorios de pago
Uso: python -m app.scripts.check_reminders_config
"""
import sys
from datetime import datetime, timedelta

try:
    from app.core.config import settings
    config_loaded = True
except Exception as e:
    print(f"❌ Error cargando configuración: {e}")
    config_loaded = False
    sys.exit(1)

# Imports opcionales (solo si están disponibles)
try:
    from app.services.scheduler_service import scheduler, schedule_immediate_check
    scheduler_available = True
except ImportError:
    scheduler_available = False
    scheduler = None
    schedule_immediate_check = None

try:
    from app.core.database import SessionLocal
    from app.models.rma import RMA, RMAStatus
    database_available = True
except ImportError:
    database_available = False
    SessionLocal = None


def print_current_config():
    """Mostrar configuración actual"""
    print("\n" + "="*60)
    print("⚙️  CONFIGURACIÓN DE RECORDATORIOS DE PAGO")
    print("="*60)
    
    print(f"\n📅 Intervalo de envío de recordatorios:")
    print(f"   └─> {settings.PAYMENT_REMINDER_INTERVAL_DAYS} días")
    
    print(f"\n🕐 Frecuencia de verificación del scheduler:")
    print(f"   └─> Cada {settings.PAYMENT_REMINDER_CHECK_INTERVAL_HOURS} horas")
    
    print(f"\n📧 Email configurado:")
    print(f"   └─> Habilitado: {settings.EMAIL_ENABLED}")
    print(f"   └─> From: {settings.EMAIL_FROM}")
    
    print(f"\n🎨 Colores de urgencia (basado en múltiplos del intervalo):")
    interval = settings.PAYMENT_REMINDER_INTERVAL_DAYS
    print(f"   🟡 Amarillo: {interval}-{interval*2-1} días")
    print(f"   🟠 Naranja:  {interval*2}-{interval*3-1} días")
    print(f"   🔴 Rojo:     {interval*3}+ días")
    
    print("\n" + "="*60)


def check_scheduler_status():
    """Verificar estado del scheduler"""
    print("\n" + "="*60)
    print("🔍 ESTADO DEL SCHEDULER")
    print("="*60)
    
    if not scheduler_available:
        print("\n⚠️  Módulos del scheduler no disponibles")
        print("   Instala todas las dependencias: pip install -r requirements.txt")
        print("\n" + "="*60)
        return
    
    if scheduler.running:
        print("\n✅ Scheduler está ACTIVO")
        
        jobs = scheduler.get_jobs()
        if jobs:
            print(f"\n📋 Jobs programados: {len(jobs)}")
            for job in jobs:
                print(f"\n   Job: {job.name}")
                print(f"   └─> ID: {job.id}")
                print(f"   └─> Próxima ejecución: {job.next_run_time}")
                print(f"   └─> Trigger: {job.trigger}")
        else:
            print("\n⚠️  No hay jobs programados")
    else:
        print("\n❌ Scheduler NO está activo")
        print("   Inicia el servidor FastAPI para activar el scheduler")
    
    print("\n" + "="*60)


def check_pending_rmas():
    """Verificar RMAs en estado PAYMENT"""
    print("\n" + "="*60)
    print("💰 RMAs EN ESTADO PAYMENT")
    print("="*60)
    
    if not database_available:
        print("\n⚠️  Módulos de base de datos no disponibles")
        print("   Instala todas las dependencias: pip install -r requirements.txt")
        print("\n" + "="*60)
        return
    
    db = SessionLocal()
    try:
        rmas = db.query(RMA).filter(RMA.status == RMAStatus.PAYMENT).all()
        
        if not rmas:
            print("\n✅ No hay RMAs pendientes de pago actualmente")
        else:
            print(f"\n📊 Total de RMAs en PAYMENT: {len(rmas)}")
            
            now = datetime.utcnow()
            interval = settings.PAYMENT_REMINDER_INTERVAL_DAYS
            
            for rma in rmas:
                print(f"\n   RMA: {rma.rma_number or f'#{rma.id}'}")
                print(f"   └─> Empresa: {rma.company_name}")
                
                # Calcular días desde último recordatorio o entrada a PAYMENT
                if rma.last_payment_reminder:
                    reference_date = rma.last_payment_reminder
                    ref_type = "último recordatorio"
                else:
                    reference_date = rma.updated_at
                    ref_type = "entrada a PAYMENT"
                
                days_passed = (now - reference_date).days
                days_until_next = interval - (days_passed % interval)
                
                print(f"   └─> Días desde {ref_type}: {days_passed}")
                print(f"   └─> Días hasta próximo recordatorio: {days_until_next}")
                
                # Indicar nivel de urgencia
                if days_passed >= (interval * 3):
                    urgency = "🔴 MUY URGENTE"
                elif days_passed >= (interval * 2):
                    urgency = "🟠 URGENTE"
                else:
                    urgency = "🟡 Normal"
                
                print(f"   └─> Urgencia: {urgency}")
    
    finally:
        db.close()
    
    print("\n" + "="*60)


def simulate_reminder_check():
    """Simular verificación de recordatorios"""
    print("\n" + "="*60)
    print("🧪 SIMULACIÓN DE VERIFICACIÓN")
    print("="*60)
    
    if not scheduler_available:
        print("\n⚠️  Función no disponible sin módulos del scheduler")
        print("   Instala todas las dependencias: pip install -r requirements.txt")
        print("\n" + "="*60)
        return
    
    response = input("\n¿Deseas forzar una verificación inmediata? (s/n): ")
    
    if response.lower() == 's':
        print("\n⚡ Programando verificación inmediata...")
        try:
            schedule_immediate_check()
            print("✅ Verificación programada exitosamente")
            print("   Revisa los logs del servidor para ver los resultados")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("\n⏭️  Verificación cancelada")
    
    print("\n" + "="*60)


def main():
    """Función principal"""
    print("\n" + "="*60)
    print("🔧 HERRAMIENTA DE VERIFICACIÓN DE RECORDATORIOS")
    print("="*60)
    
    while True:
        print("\n¿Qué deseas hacer?")
        print("1. Ver configuración actual")
        print("2. Verificar estado del scheduler")
        print("3. Ver RMAs en estado PAYMENT")
        print("4. Forzar verificación inmediata")
        print("5. Ver todo (opciones 1-3)")
        print("0. Salir")
        
        choice = input("\nSelecciona una opción: ")
        
        if choice == "1":
            print_current_config()
        elif choice == "2":
            check_scheduler_status()
        elif choice == "3":
            check_pending_rmas()
        elif choice == "4":
            simulate_reminder_check()
        elif choice == "5":
            print_current_config()
            check_scheduler_status()
            check_pending_rmas()
        elif choice == "0":
            print("\n👋 ¡Hasta luego!")
            break
        else:
            print("\n❌ Opción inválida. Intenta de nuevo.")
        
        input("\n[Presiona Enter para continuar...]")


if __name__ == "__main__":
    main()
