# 📡 WebSocket - Resumen Completo de Notificaciones

## ✅ Notificaciones Implementadas

### **1. Nuevo RMA Creado** ✅
**Trigger:** Cuando un usuario crea un RMA  
**Endpoint:** `POST /api/v1/rmas`  
**Quién recibe:**
- ✅ SUPERADMIN (todos los RMAs)
- ✅ ADMIN del país del RMA

**Payload:**
```json
{
  "type": "new_rma",
  "data": {
    "id": 123,
    "rma_number": null,
    "status": "rma_submitted",
    "company_name": "Hammond and Vaughn Co",
    "company_address": "75b",
    "postal_code": "11100",
    "country_id": 2,
    "country_name": "Colombia",
    "created_by": "user@example.com",
    "created_at": "2024-11-13T10:30:00Z",
    "total_items": 1
  },
  "timestamp": "2024-11-13T10:30:00Z"
}
```

---

### **2. Estado de RMA Cambiado** ✅
**Trigger:** Cuando un admin/superadmin cambia el estado del RMA  
**Endpoint:** `PUT /api/v1/rmas/{id}/status`  
**Quién recibe:**
- ✅ SUPERADMIN (todos los RMAs)
- ✅ ADMIN del país del RMA  
- ✅ USER del país del RMA

**Payload:**
```json
{
  "type": "rma_status_changed",
  "data": {
    "id": 123,
    "rma_number": "RMA-CO-2024-001",
    "status": "approved",
    "company_name": "Hammond and Vaughn Co",
    "company_address": "75b",
    "postal_code": "11100",
    "country_id": 2,
    "country_name": "Colombia",
    "updated_by": "admin@example.com",
    "updated_at": "2024-11-13T11:00:00Z",
    "shipping_company": null,
    "tracking_id": null,
    "total_items": 1
  },
  "timestamp": "2024-11-13T11:00:00Z"
}
```

---

## 🎯 Casos de Uso

### **Caso 1: Usuario crea RMA**
```
USER (Colombia) → Crea RMA
    ↓
SUPERADMIN → 🔔 Recibe notificación "new_rma"
ADMIN (Colombia) → 🔔 Recibe notificación "new_rma"
ADMIN (México) → ❌ NO recibe (diferente país)
```

### **Caso 2: Admin aprueba RMA**
```
ADMIN (Colombia) → Cambia estado a "approved"
    ↓
SUPERADMIN → 🔔 Recibe notificación "rma_status_changed"
ADMIN (Colombia) → 🔔 Recibe notificación "rma_status_changed"
USER (Colombia) → 🔔 Recibe notificación "rma_status_changed"
USER (México) → ❌ NO recibe (diferente país)
```

### **Caso 3: Superadmin ve todo**
```
Cualquier RMA en cualquier país
    ↓
SUPERADMIN → ✅ SIEMPRE recibe notificaciones
```

---

## 📊 Estados de RMA Disponibles

| Estado | Valor | Descripción |
|--------|-------|-------------|
| RMA Enviado | `rma_submitted` | RMA creado por usuario |
| Esperando Mercancía | `awaiting_goods` | Esperando que lleguen los productos |
| Evaluando | `evaluating` | En proceso de evaluación |
| Procesando | `processing` | Procesando la solicitud |
| Pago | `payment` | Esperando pago del cliente |
| En Envío | `in_shipping` | Productos en tránsito |
| **Aprobado** | `approved` | ✅ RMA aprobado |
| **Rechazado** | `rejected` | ❌ RMA rechazado |
| En Reparación | `in_repair` | Producto en reparación |
| Completado | `completed` | RMA finalizado |

---

## 🔔 Frontend - Cómo Manejar las Notificaciones

### **React Hook Completo**

```typescript
import { useEffect } from 'react';
import { toast } from 'react-toastify';
import { useQueryClient } from '@tanstack/react-query';

function useRMAWebSocketHandler(messages: WebSocketMessage[]) {
  const queryClient = useQueryClient();
  
  useEffect(() => {
    const lastMessage = messages[messages.length - 1];
    if (!lastMessage) return;
    
    // 🆕 Nuevo RMA creado
    if (lastMessage.type === 'new_rma') {
      const { company_name, rma_number, country_name } = lastMessage.data;
      
      toast.info(
        `🆕 Nuevo RMA: ${company_name} (${country_name})`,
        {
          position: 'top-right',
          autoClose: 5000,
          onClick: () => {
            // Navegar al RMA
            navigate(`/rmas/${lastMessage.data.id}`);
          }
        }
      );
      
      // Refrescar lista de RMAs
      queryClient.invalidateQueries(['rmas']);
    }
    
    // 🔄 Estado de RMA cambiado
    if (lastMessage.type === 'rma_status_changed') {
      const { rma_number, status, company_name } = lastMessage.data;
      
      // Diferentes notificaciones según el estado
      switch (status) {
        case 'approved':
          toast.success(
            `✅ RMA ${rma_number || 'Sin número'} APROBADO - ${company_name}`,
            { autoClose: 7000 }
          );
          break;
          
        case 'rejected':
          toast.error(
            `❌ RMA ${rma_number || 'Sin número'} RECHAZADO - ${company_name}`,
            { autoClose: 7000 }
          );
          break;
          
        case 'in_shipping':
          toast.info(
            `📦 RMA ${rma_number} EN ENVÍO - ${company_name}`,
            { autoClose: 5000 }
          );
          break;
          
        case 'payment':
          toast.warning(
            `💳 RMA ${rma_number} - PAGO PENDIENTE - ${company_name}`,
            { autoClose: 5000 }
          );
          break;
          
        default:
          toast.info(
            `🔄 RMA ${rma_number} → ${status}`,
            { autoClose: 4000 }
          );
      }
      
      // Refrescar lista y detalle
      queryClient.invalidateQueries(['rmas']);
      queryClient.invalidateQueries(['rma', lastMessage.data.id]);
    }
    
  }, [messages, queryClient, navigate]);
}
```

### **Badge de Notificaciones No Leídas**

```typescript
function RMADashboard() {
  const [unreadCount, setUnreadCount] = useState(0);
  const { messages } = useRMANotifications(token);
  
  useEffect(() => {
    // Contar mensajes no leídos
    const unread = messages.filter(m => !m.read).length;
    setUnreadCount(unread);
    
    // Actualizar título del documento
    document.title = unread > 0 
      ? `(${unread}) RMA Dashboard` 
      : 'RMA Dashboard';
  }, [messages]);
  
  return (
    <div>
      <h1>
        RMAs
        {unreadCount > 0 && (
          <span className="badge bg-danger">{unreadCount}</span>
        )}
      </h1>
    </div>
  );
}
```

### **Sonido de Notificación**

```typescript
const playNotificationSound = () => {
  const audio = new Audio('/notification.mp3');
  audio.play().catch(err => console.log('No se pudo reproducir sonido'));
};

// Usar en el handler
if (lastMessage.type === 'new_rma') {
  playNotificationSound();
  toast.info(...);
}
```

---

## 🧪 Testing Paso a Paso

### **Test 1: Notificación de Nuevo RMA**

1. **Terminal 1:** Conecta WebSocket como ADMIN
   ```bash
   # Postman WebSocket
   ws://localhost:8000/api/v1/ws?token=ADMIN_TOKEN
   ```

2. **Terminal 2:** Crea RMA como USER (mismo país)
   ```bash
   curl -X POST http://localhost:8000/api/v1/rmas?country_id=2 \
     -H "Authorization: Bearer USER_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "company_name": "Test Company",
       "company_address": "123 Street",
       "postal_code": "11100",
       "items": [...]
     }'
   ```

3. **Terminal 1:** ⚡ Deberías recibir notificación `new_rma` inmediatamente

---

### **Test 2: Notificación de Cambio de Estado**

1. **Terminal 1:** Conecta WebSocket como USER
   ```bash
   ws://localhost:8000/api/v1/ws?token=USER_TOKEN
   ```

2. **Terminal 2:** Cambia estado del RMA como ADMIN
   ```bash
   curl -X PUT http://localhost:8000/api/v1/rmas/123/status \
     -H "Authorization: Bearer ADMIN_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "new_status": "approved",
       "comment": "Todo correcto, aprobado"
     }'
   ```

3. **Terminal 1:** ⚡ Deberías recibir notificación `rma_status_changed` inmediatamente

---

### **Test 3: Filtrado por País**

1. **Terminal 1:** Conecta como ADMIN de México
2. **Terminal 2:** Crea RMA en Colombia
3. **Terminal 1:** ❌ NO deberías recibir notificación (diferente país)
4. **Terminal 3:** Conecta como SUPERADMIN
5. **Terminal 3:** ✅ SÍ recibe la notificación (ve todos los países)

---

## 📊 Logs del Backend

Cuando todo funciona correctamente:

```
INFO: WebSocket connected: role=admin, countries=[1, 2]
INFO: New RMA notification sent: RMA ID=123, Country=2
INFO: RMA status change notification sent: RMA ID=123, Status=approved
INFO: WebSocket disconnected: role=admin, countries=[1, 2]
```

---

## 🔧 Archivos Modificados

### **Backend:**
- ✅ `app/core/websocket.py` - Gestor de conexiones
- ✅ `app/api/v1/endpoints/websocket.py` - Endpoint WS
- ✅ `app/api/v1/endpoints/rmas.py` - Notificaciones en create y update_status
- ✅ `app/api/v1/router.py` - Registro del router

### **Documentación:**
- ✅ `WEBSOCKET_GUIDE.md` - Guía completa para frontend
- ✅ `WEBSOCKET_TESTING.md` - Instrucciones de testing
- ✅ `WEBSOCKET_SUMMARY.md` - Este resumen
- ✅ `test_websocket.py` - Script de pruebas

---

## 🔮 Futuras Mejoras

- [ ] Notificaciones de comentarios en RMAs
- [ ] Notificaciones de archivos adjuntos
- [ ] Notificaciones de recordatorios de pago automáticos
- [ ] Sala de chat por RMA específico
- [ ] Indicador "usuario escribiendo..."
- [ ] Historial persistente de notificaciones
- [ ] Preferencias de notificaciones por usuario

---

## ✨ Resumen

| Feature | Estado |
|---------|--------|
| Notificación de nuevo RMA | ✅ Implementado |
| Notificación de cambio de estado | ✅ Implementado |
| Filtrado por rol | ✅ Implementado |
| Filtrado por país | ✅ Implementado |
| Autenticación JWT | ✅ Implementado |
| Reconexión automática | ✅ Documentado |
| Tests | ✅ Pasando |
| Documentación | ✅ Completa |

---

¡Sistema de notificaciones WebSocket completamente funcional! 🎉🚀
