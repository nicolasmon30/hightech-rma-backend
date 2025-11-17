# 🧪 Testing WebSocket - Guía Rápida

## Probar con Postman/Insomnia

### **Paso 1: Obtener Token JWT**

**Request:**
```http
POST http://localhost:8000/api/v1/auth/login
Content-Type: application/json

{
  "username": "admin@example.com",
  "password": "tu_password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

Copia el valor de `access_token`.

---

### **Paso 2: Conectar WebSocket**

**En Postman:**
1. New → WebSocket Request
2. URL: `ws://localhost:8000/api/v1/ws?token=TU_TOKEN_AQUI`
3. Click **Connect**

**Deberías recibir:**
```json
{
  "type": "connection_established",
  "message": "Conectado como admin",
  "user_id": 1,
  "role": "admin",
  "countries": [...]
}
```

---

### **Paso 3: Probar Ping/Pong**

**Enviar:**
```
ping
```

**Recibirás:**
```json
{
  "type": "pong",
  "timestamp": null
}
```

---

### **Paso 4: Crear un RMA (en otro cliente)**

**Request:**
```http
POST http://localhost:8000/api/v1/rmas?country_id=1
Authorization: Bearer TU_TOKEN
Content-Type: application/json

{
  "company_name": "Hammond and Vaughn Co",
  "company_address": "75b Street, Building A",
  "postal_code": "11100",
  "items": [
    {
      "brand_id": 1,
      "product_id": 1,
      "model_id": 1,
      "serial_number": "SN123456",
      "service_type": "repair",
      "issue_description": "Equipo no enciende"
    }
  ]
}
```

---

### **Paso 5: Ver Notificación en WebSocket**

**En tu conexión WebSocket activa recibirás:**
```json
{
  "type": "new_rma",
  "data": {
    "id": 123,
    "rma_number": null,
    "status": "rma_submitted",
    "company_name": "Hammond and Vaughn Co",
    "company_address": "75b Street, Building A",
    "postal_code": "11100",
    "country_id": 1,
    "country_name": "México",
    "created_by": "admin@example.com",
    "created_at": "2024-11-13T10:30:00Z",
    "total_items": 1
  },
  "timestamp": "2024-11-13T10:30:00Z"
}
```

---

## Probar con JavaScript (Browser Console)

Abre la consola del navegador (F12) y ejecuta:

```javascript
// 1. Reemplaza con tu token
const token = "eyJ0eXAiOiJKV1QiLCJhbGc...";

// 2. Conectar
const ws = new WebSocket(`ws://localhost:8000/api/v1/ws?token=${token}`);

// 3. Escuchar eventos
ws.onopen = () => {
  console.log("✅ Conectado");
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log("📩 Mensaje:", message);
  
  if (message.type === 'new_rma') {
    alert(`Nuevo RMA: ${message.data.company_name}`);
  }
};

ws.onerror = (error) => {
  console.error("❌ Error:", error);
};

ws.onclose = () => {
  console.log("🔌 Desconectado");
};

// 4. Enviar ping
ws.send("ping");
```

---

## Testing Automático

Ejecuta el script de prueba:

```bash
python test_websocket.py
```

**Output esperado:**
```
============================================================
WebSocket Manager - Test Suite
============================================================
🧪 Probando ConnectionManager...
✅ Roles registrados: ['superadmin', 'admin', 'user']
✅ Conexiones por país: 0

📡 Probando notificación de nuevo RMA...
✅ Notificación enviada (sin conexiones activas, es normal)

✅ Todas las pruebas pasaron correctamente!
🚀 WebSocket está listo para usar

✅ TEST PASSED
```

---

## Verificar Logs del Servidor

Cuando conectas/desconectas WebSocket, deberías ver:

```
INFO:     WebSocket connected: role=admin, countries=[1, 2]
INFO:     New RMA notification sent: RMA ID=123, Country=1
INFO:     WebSocket disconnected: role=admin, countries=[1, 2]
```

---

## Troubleshooting

### ❌ "Could not connect to WebSocket"
- Verifica que el servidor esté corriendo: `uvicorn app.main:app --reload`
- Usa `ws://` no `wss://` (para desarrollo local)

### ❌ "Connection closed: 1008"
- Token JWT inválido o expirado
- Obtén un nuevo token haciendo login

### ❌ No recibo notificaciones
- Verifica que tu rol tenga acceso al país del RMA
- SUPERADMIN: recibe todas
- ADMIN/USER: solo de sus países

---

## Demo Completo

1. **Terminal 1:** Inicia el servidor
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Terminal 2 (o Postman):** Conecta WebSocket
   ```
   ws://localhost:8000/api/v1/ws?token=...
   ```

3. **Terminal 3 (o Postman):** Crea un RMA
   ```bash
   curl -X POST http://localhost:8000/api/v1/rmas?country_id=1 \
     -H "Authorization: Bearer TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"customer_name":"Test","customer_email":"test@test.com",...}'
   ```

4. **Ver en Terminal 2:** Notificación recibida instantáneamente ⚡

---

## 🎯 Escenarios de Prueba

| Escenario | Usuario Conectado | RMA Creado en | ¿Recibe Notificación? |
|-----------|-------------------|---------------|----------------------|
| SUPERADMIN conectado | Superadmin | País México | ✅ Sí |
| ADMIN México conectado | Admin México | País México | ✅ Sí |
| ADMIN México conectado | Admin México | País Colombia | ❌ No |
| USER México conectado | User México | País México | ✅ Sí |
| USER México conectado | User México | País Colombia | ❌ No |

---

¡Listo para usar! 🚀
