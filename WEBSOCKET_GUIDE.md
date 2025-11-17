# WebSocket - Notificaciones en Tiempo Real

## 📡 Implementación de WebSockets para RMAs

Este sistema permite recibir notificaciones en tiempo real cuando se crean nuevos RMAs.

---

## 🔌 Conexión WebSocket

### **URL del WebSocket**
```
ws://localhost:8000/api/v1/ws?token=YOUR_JWT_TOKEN
```

### **Autenticación**
El token JWT se envía como query parameter en la URL de conexión.

---

## 🎯 Eventos que Recibes

### **1. Confirmación de Conexión**
Cuando te conectas exitosamente, recibes:
```json
{
  "type": "connection_established",
  "message": "Conectado como admin",
  "user_id": 123,
  "role": "admin",
  "countries": [
    { "id": 1, "name": "México" },
    { "id": 2, "name": "Colombia" }
  ]
}
```

### **2. Nuevo RMA Creado**
Cuando alguien crea un RMA, recibes:
```json
{
  "type": "new_rma",
  "data": {
    "id": 456,
    "rma_number": null,
    "status": "rma_submitted",
    "company_name": "Hammond and Vaughn Co",
    "company_address": "75b",
    "postal_code": "11100",
    "country_id": 1,
    "country_name": "México",
    "created_by": "user@example.com",
    "created_at": "2024-11-13T10:30:00Z",
    "total_items": 3
  },
  "timestamp": "2024-11-13T10:30:00Z"
}
```

### **3. Cambio de Estado de RMA**
Cuando cambia el estado de un RMA:
```json
{
  "type": "rma_status_changed",
  "data": {
    "id": 456,
    "rma_number": "RMA-MX-2024-001",
    "status": "APPROVED",
    "updated_at": "2024-11-13T11:00:00Z"
  },
  "timestamp": "2024-11-13T11:00:00Z"
}
```

---

## 🚀 Implementación en Frontend

### **React con Native WebSocket**

```typescript
import { useEffect, useState } from 'react';

interface WebSocketMessage {
  type: 'connection_established' | 'new_rma' | 'rma_status_changed';
  data?: any;
  timestamp?: string;
}

export const useRMANotifications = (token: string) => {
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    if (!token) return;

    // Conectar WebSocket
    const websocket = new WebSocket(
      `ws://localhost:8000/api/v1/ws?token=${token}`
    );

    websocket.onopen = () => {
      console.log('✅ WebSocket conectado');
      setIsConnected(true);
    };

    websocket.onmessage = (event) => {
      const message: WebSocketMessage = JSON.parse(event.data);
      console.log('📩 Mensaje recibido:', message);
      
      setMessages((prev) => [...prev, message]);

      // Manejar diferentes tipos de mensajes
      switch (message.type) {
        case 'connection_established':
          console.log('✅ Conexión establecida:', message);
          break;
        
        case 'new_rma':
          console.log('🆕 Nuevo RMA creado:', message.data);
          // Aquí puedes mostrar una notificación toast
          // Ejemplo: toast.success(`Nuevo RMA: ${message.data.company_name}`)
          // Actualizar lista de RMAs
          break;
        
        case 'rma_status_changed':
          console.log('🔄 Estado de RMA cambiado:', message.data);
          // Actualizar el RMA específico en la UI
          break;
      }
    };

    websocket.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
      setIsConnected(false);
    };

    websocket.onclose = () => {
      console.log('🔌 WebSocket desconectado');
      setIsConnected(false);
    };

    setWs(websocket);

    // Cleanup al desmontar
    return () => {
      websocket.close();
    };
  }, [token]);

  // Función para enviar ping (mantener conexión viva)
  const sendPing = () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send('ping');
    }
  };

  return { messages, isConnected, sendPing };
};
```

### **Uso en Componente**

```typescript
import { useRMANotifications } from './hooks/useRMANotifications';
import { toast } from 'react-toastify';

function AdminDashboard() {
  const token = localStorage.getItem('access_token');
  const { messages, isConnected } = useRMANotifications(token);

  useEffect(() => {
    // Procesar nuevos mensajes
    const lastMessage = messages[messages.length - 1];
    
    if (lastMessage?.type === 'new_rma') {
      const rma = lastMessage.data;
      
      // Mostrar notificación
      toast.success(
        `Nuevo RMA creado: ${rma.rma_number || 'Sin número'} - ${rma.company_name}`,
        {
          position: 'top-right',
          autoClose: 5000,
        }
      );
      
      // Refrescar lista de RMAs
      queryClient.invalidateQueries(['rmas']);
    }
  }, [messages]);

  return (
    <div>
      {/* Indicador de conexión */}
      <div className="connection-status">
        {isConnected ? '🟢 Conectado' : '🔴 Desconectado'}
      </div>
      
      {/* Tu UI aquí */}
    </div>
  );
}
```

---

## 🔒 Permisos y Notificaciones

| Rol | Notificaciones que Recibe |
|-----|---------------------------|
| **SUPERADMIN** | Todos los RMAs de todos los países |
| **ADMIN** | RMAs de su(s) país(es) asignado(s) |
| **USER** | RMAs de su(s) país(es) asignado(s) |

---

## 💡 Mejores Prácticas

### **1. Reconexión Automática**
```typescript
const connectWithRetry = (token: string, retries = 5) => {
  let attempt = 0;
  
  const connect = () => {
    const ws = new WebSocket(`ws://localhost:8000/api/v1/ws?token=${token}`);
    
    ws.onclose = () => {
      if (attempt < retries) {
        attempt++;
        console.log(`Reintentando conexión (${attempt}/${retries})...`);
        setTimeout(connect, 2000 * attempt); // Backoff exponencial
      }
    };
    
    return ws;
  };
  
  return connect();
};
```

### **2. Heartbeat (Ping/Pong)**
```typescript
useEffect(() => {
  if (!isConnected) return;
  
  // Enviar ping cada 30 segundos
  const interval = setInterval(() => {
    sendPing();
  }, 30000);
  
  return () => clearInterval(interval);
}, [isConnected]);
```

### **3. Manejo de Errores**
```typescript
websocket.onerror = (error) => {
  console.error('WebSocket error:', error);
  toast.error('Error en conexión de notificaciones');
};
```

---

## 🧪 Testing con Postman/Insomnia

1. **Obtén tu token JWT** haciendo login en `/api/v1/auth/login`
2. **Crea una nueva conexión WebSocket:**
   ```
   ws://localhost:8000/api/v1/ws?token=eyJ0eXAiOiJKV1QiLCJhbGc...
   ```
3. **Envía "ping"** para verificar conexión (recibirás "pong")
4. **Crea un RMA** desde otro cliente/Postman
5. **Observa la notificación** en tu conexión WebSocket

---

## 🐛 Troubleshooting

### **Error: "WebSocket connection failed"**
- Verifica que el token JWT sea válido
- Asegúrate de usar `ws://` (no `http://`)
- Revisa que el backend esté corriendo

### **No recibo notificaciones**
- Verifica que tu rol tenga acceso al país del RMA
- Revisa los logs del backend
- Confirma que la conexión WebSocket esté activa (`isConnected === true`)

### **Desconexiones frecuentes**
- Implementa reconexión automática
- Usa heartbeat (ping/pong) cada 30 segundos
- Verifica tu conexión de red

---

## 📊 Monitoreo

Puedes ver las conexiones activas en los logs del backend:
```
INFO:     WebSocket connected: role=admin, countries=[1, 2]
INFO:     New RMA notification sent: RMA ID=456, Country=1
INFO:     WebSocket disconnected: role=admin, countries=[1, 2]
```

---

## 🔮 Futuras Mejoras

- [ ] Notificaciones de comentarios en RMAs
- [ ] Notificaciones de archivos adjuntos
- [ ] Notificaciones de recordatorios de pago
- [ ] Filtrado de notificaciones por preferencias de usuario
- [ ] Historial de notificaciones
