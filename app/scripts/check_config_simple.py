"""
Script simple para verificar configuración de recordatorios
Solo requiere python-dotenv y pydantic-settings
"""
import os
from pathlib import Path

# Cargar .env manualmente
env_path = Path(__file__).parent.parent.parent / ".env"

if env_path.exists():
    print("✅ Archivo .env encontrado\n")
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("="*60)
    print("⚙️  CONFIGURACIÓN DE RECORDATORIOS DE PAGO")
    print("="*60)
    
    # Buscar variables relevantes
    reminder_interval = None
    check_interval = None
    email_enabled = None
    email_from = None
    
    for line in lines:
        line = line.strip()
        if line.startswith('#') or not line:
            continue
        
        if 'PAYMENT_REMINDER_INTERVAL_DAYS' in line:
            reminder_interval = line.split('=')[1].strip()
        elif 'PAYMENT_REMINDER_CHECK_INTERVAL_HOURS' in line:
            check_interval = line.split('=')[1].strip()
        elif 'EMAIL_ENABLED' in line and '=' in line:
            email_enabled = line.split('=')[1].strip()
        elif 'EMAIL_FROM' in line and '=' in line:
            email_from = line.split('=')[1].strip()
    
    print(f"\n📅 Intervalo de envío de recordatorios:")
    if reminder_interval:
        print(f"   └─> {reminder_interval} días")
        interval_days = int(reminder_interval)
    else:
        print(f"   └─> 3 días (default - no configurado)")
        interval_days = 3
    
    print(f"\n🕐 Frecuencia de verificación del scheduler:")
    if check_interval:
        print(f"   └─> Cada {check_interval} horas")
    else:
        print(f"   └─> Cada 24 horas (default - no configurado)")
    
    print(f"\n📧 Email configurado:")
    print(f"   └─> Habilitado: {email_enabled if email_enabled else 'No configurado'}")
    print(f"   └─> From: {email_from if email_from else 'No configurado'}")
    
    print(f"\n🎨 Colores de urgencia (basado en múltiplos del intervalo):")
    print(f"   🟡 Amarillo: {interval_days}-{interval_days*2-1} días")
    print(f"   🟠 Naranja:  {interval_days*2}-{interval_days*3-1} días")
    print(f"   🔴 Rojo:     {interval_days*3}+ días")
    
    print("\n" + "="*60)
    
    # Recomendaciones
    print("\n💡 RECOMENDACIONES:")
    if reminder_interval and int(reminder_interval) == 1:
        print("   ⚠️  Intervalo de 1 día - Solo para testing")
        print("   📝 Para producción considera: 3-5 días")
    
    if check_interval and int(check_interval) == 1:
        print("   ⚠️  Verificación cada 1 hora - Solo para testing")
        print("   📝 Para producción considera: 24 horas")
    
    if not reminder_interval or not check_interval:
        print("   ℹ️  Agrega estas líneas a tu .env:")
        if not reminder_interval:
            print("      PAYMENT_REMINDER_INTERVAL_DAYS=3")
        if not check_interval:
            print("      PAYMENT_REMINDER_CHECK_INTERVAL_HOURS=24")
    
    print("\n" + "="*60)
    print("\n📚 Documentación completa:")
    print("   └─> docs/PAYMENT_REMINDERS_QUICK_START.md")
    print("   └─> docs/PAYMENT_REMINDERS_CONFIG.md")
    print("   └─> docs/PAYMENT_REMINDERS_EXAMPLES.md")
    
else:
    print("❌ Archivo .env no encontrado")
    print(f"   Buscado en: {env_path}")
    print("\n💡 Crea el archivo .env basándote en .env.example")
