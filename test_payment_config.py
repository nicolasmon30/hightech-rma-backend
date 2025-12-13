"""
Script de prueba para la funcionalidad de configuración de recordatorios de pago
Verifica que los endpoints de configuración funcionen correctamente
"""
import requests
import json

# Configuración
BASE_URL = "http://localhost:8000/api/v1"
SUPERADMIN_EMAIL = "superadmin@example.com"  # Actualizar con tu email de superadmin
SUPERADMIN_PASSWORD = "your_password"  # Actualizar con tu contraseña

def login(email: str, password: str):
    """Login y obtener token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": email,
            "password": password
        }
    )
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Login exitoso")
        return data["access_token"]
    else:
        print(f"❌ Error en login: {response.status_code}")
        print(response.text)
        return None

def get_payment_reminder_config(token: str):
    """Obtener configuración actual de recordatorios"""
    response = requests.get(
        f"{BASE_URL}/system-config/payment-reminders",
        headers={"Authorization": f"Bearer {token}"}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Configuración actual:")
        print(f"   - Días entre recordatorios: {data['payment_reminder_interval_days']}")
        print(f"   - Frecuencia de verificación (horas): {data['payment_reminder_check_interval_hours']}")
        return data
    else:
        print(f"❌ Error obteniendo configuración: {response.status_code}")
        print(response.text)
        return None

def update_payment_reminder_config(token: str, days: int, hours: int):
    """Actualizar configuración de recordatorios"""
    response = requests.put(
        f"{BASE_URL}/system-config/payment-reminders",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "payment_reminder_interval_days": days,
            "payment_reminder_check_interval_hours": hours
        }
    )
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Configuración actualizada:")
        print(f"   - Días entre recordatorios: {data['payment_reminder_interval_days']}")
        print(f"   - Frecuencia de verificación (horas): {data['payment_reminder_check_interval_hours']}")
        return data
    else:
        print(f"❌ Error actualizando configuración: {response.status_code}")
        print(response.text)
        return None

def get_all_configs(token: str):
    """Obtener todas las configuraciones del sistema"""
    response = requests.get(
        f"{BASE_URL}/system-config/",
        headers={"Authorization": f"Bearer {token}"}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Todas las configuraciones ({len(data)}):")
        for config in data:
            print(f"   - {config['key']}: {config['value']}")
        return data
    else:
        print(f"❌ Error obteniendo configuraciones: {response.status_code}")
        print(response.text)
        return None

def main():
    print("=" * 60)
    print("TEST: Configuración de Recordatorios de Pago")
    print("=" * 60)
    
    # 1. Login
    print("\n1. Login como SUPERADMIN...")
    token = login(SUPERADMIN_EMAIL, SUPERADMIN_PASSWORD)
    if not token:
        print("❌ No se pudo obtener token. Verifica credenciales.")
        return
    
    # 2. Obtener configuración actual
    print("\n2. Obtener configuración actual...")
    current_config = get_payment_reminder_config(token)
    
    # 3. Actualizar configuración
    print("\n3. Actualizar configuración (5 días, 12 horas)...")
    updated_config = update_payment_reminder_config(token, days=5, hours=12)
    
    # 4. Verificar que se actualizó
    print("\n4. Verificar actualización...")
    verified_config = get_payment_reminder_config(token)
    
    # 5. Restaurar valores originales (opcional)
    if current_config:
        print("\n5. Restaurar valores originales...")
        update_payment_reminder_config(
            token,
            days=current_config['payment_reminder_interval_days'],
            hours=current_config['payment_reminder_check_interval_hours']
        )
    
    # 6. Ver todas las configuraciones
    print("\n6. Ver todas las configuraciones del sistema...")
    get_all_configs(token)
    
    print("\n" + "=" * 60)
    print("✅ Test completado")
    print("=" * 60)

if __name__ == "__main__":
    main()
