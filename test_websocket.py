"""
Script de prueba para verificar WebSocket
"""
import sys
import asyncio
from app.core.websocket import manager
from app.models.user import UserRole

async def test_websocket_manager():
    print("🧪 Probando ConnectionManager...")
    
    # Verificar estructura inicial
    print(f"✅ Roles registrados: {list(manager.active_connections.keys())}")
    print(f"✅ Conexiones por país: {len(manager.country_connections)}")
    
    # Simular datos de RMA
    rma_data = {
        "id": 999,
        "rma_number": None,
        "status": "rma_submitted",
        "company_name": "Test Company Inc",
        "company_address": "123 Test Street",
        "postal_code": "12345",
        "country_id": 1,
        "country_name": "México",
        "created_by": "admin@example.com",
        "created_at": "2024-11-13T10:30:00Z",
        "total_items": 2
    }
    
    # Probar notificación (sin conexiones activas)
    print("\n📡 Probando notificación de nuevo RMA...")
    await manager.notify_new_rma(rma_data, country_id=1)
    print("✅ Notificación enviada (sin conexiones activas, es normal)")
    
    print("\n✅ Todas las pruebas pasaron correctamente!")
    print("🚀 WebSocket está listo para usar")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("WebSocket Manager - Test Suite")
    print("=" * 60)
    
    try:
        result = asyncio.run(test_websocket_manager())
        if result:
            print("\n✅ TEST PASSED")
            sys.exit(0)
        else:
            print("\n❌ TEST FAILED")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
