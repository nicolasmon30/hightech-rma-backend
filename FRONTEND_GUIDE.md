# 🎯 Guía para el Frontend: Configuración de Recordatorios de Pago

## 📌 Resumen
El superadministrador ahora puede modificar los parámetros de recordatorios de pago desde el frontend. Esta guía te ayudará a implementar la interfaz.

## 🔑 Requisitos Previos
- Usuario autenticado con rol **SUPERADMIN**
- Token JWT válido

## 🌐 Endpoints Disponibles

### 1️⃣ Obtener Configuración Actual

**Request:**
```http
GET /api/v1/system-config/payment-reminders
Authorization: Bearer YOUR_JWT_TOKEN
```

**Response (200 OK):**
```json
{
  "payment_reminder_interval_days": 3,
  "payment_reminder_check_interval_hours": 24
}
```

**Errores Comunes:**
- `401 Unauthorized`: Token inválido o expirado
- `403 Forbidden`: Usuario no es SUPERADMIN

---

### 2️⃣ Actualizar Configuración

**Request:**
```http
PUT /api/v1/system-config/payment-reminders
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json

{
  "payment_reminder_interval_days": 5,
  "payment_reminder_check_interval_hours": 12
}
```

**Response (200 OK):**
```json
{
  "payment_reminder_interval_days": 5,
  "payment_reminder_check_interval_hours": 12
}
```

**Validaciones:**
- `payment_reminder_interval_days`: Entero entre 1 y 30
- `payment_reminder_check_interval_hours`: Entero entre 1 y 168

**Errores Comunes:**
- `422 Unprocessable Entity`: Valores fuera de rango
- `401 Unauthorized`: Token inválido
- `403 Forbidden`: Usuario no es SUPERADMIN

---

## 💻 Implementación en React

### Componente Completo

```jsx
import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from './config';

function PaymentReminderSettings() {
  const [config, setConfig] = useState({
    payment_reminder_interval_days: 3,
    payment_reminder_check_interval_hours: 24
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  // Obtener token del contexto/store
  const token = localStorage.getItem('token'); // Ajustar según tu implementación

  // Cargar configuración al montar el componente
  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(
        `${API_BASE_URL}/system-config/payment-reminders`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) {
        throw new Error('Error al obtener la configuración');
      }

      const data = await response.json();
      setConfig(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const response = await fetch(
        `${API_BASE_URL}/system-config/payment-reminders`,
        {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(config)
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al guardar la configuración');
      }

      const data = await response.json();
      setConfig(data);
      setSuccess(true);
      
      // Ocultar mensaje de éxito después de 3 segundos
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field, value) => {
    const numValue = parseInt(value, 10);
    
    // Validar rangos
    if (field === 'payment_reminder_interval_days') {
      if (numValue >= 1 && numValue <= 30) {
        setConfig({ ...config, [field]: numValue });
      }
    } else if (field === 'payment_reminder_check_interval_hours') {
      if (numValue >= 1 && numValue <= 168) {
        setConfig({ ...config, [field]: numValue });
      }
    }
  };

  return (
    <div className="payment-reminder-settings">
      <h2>Configuración de Recordatorios de Pago</h2>
      
      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}
      
      {success && (
        <div className="alert alert-success">
          Configuración actualizada correctamente. El scheduler se ha reiniciado.
        </div>
      )}

      <div className="form-group">
        <label htmlFor="days">
          Días entre recordatorios (1-30):
        </label>
        <input
          id="days"
          type="number"
          min="1"
          max="30"
          value={config.payment_reminder_interval_days}
          onChange={(e) => handleChange('payment_reminder_interval_days', e.target.value)}
          disabled={loading}
        />
        <small>
          Los recordatorios se enviarán cada {config.payment_reminder_interval_days} día(s)
        </small>
      </div>

      <div className="form-group">
        <label htmlFor="hours">
          Frecuencia de verificación (1-168 horas):
        </label>
        <input
          id="hours"
          type="number"
          min="1"
          max="168"
          value={config.payment_reminder_check_interval_hours}
          onChange={(e) => handleChange('payment_reminder_check_interval_hours', e.target.value)}
          disabled={loading}
        />
        <small>
          El sistema verificará cada {config.payment_reminder_check_interval_hours} hora(s)
        </small>
      </div>

      <button 
        onClick={handleSave} 
        disabled={loading}
        className="btn btn-primary"
      >
        {loading ? 'Guardando...' : 'Guardar Configuración'}
      </button>
    </div>
  );
}

export default PaymentReminderSettings;
```

---

## 🎨 Estilos CSS Sugeridos

```css
.payment-reminder-settings {
  max-width: 600px;
  margin: 2rem auto;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.payment-reminder-settings h2 {
  margin-bottom: 1.5rem;
  color: #333;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #555;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-group input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.form-group small {
  display: block;
  margin-top: 0.5rem;
  color: #666;
  font-size: 0.875rem;
}

.alert {
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.alert-error {
  background-color: #fee;
  color: #c33;
  border: 1px solid #fcc;
}

.alert-success {
  background-color: #efe;
  color: #3c3;
  border: 1px solid #cfc;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0056b3;
}

.btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
```

---

## 🔒 Protección de Ruta

Solo usuarios SUPERADMIN deben ver esta página:

```jsx
import { Navigate } from 'react-router-dom';

function ProtectedPaymentSettings() {
  const user = useAuth(); // Hook para obtener usuario actual
  
  if (user.role !== 'SUPERADMIN') {
    return <Navigate to="/dashboard" />;
  }
  
  return <PaymentReminderSettings />;
}
```

---

## 🧪 Testing con TypeScript

```typescript
interface PaymentReminderConfig {
  payment_reminder_interval_days: number;
  payment_reminder_check_interval_hours: number;
}

class PaymentReminderService {
  private baseUrl: string;
  private token: string;

  constructor(baseUrl: string, token: string) {
    this.baseUrl = baseUrl;
    this.token = token;
  }

  async getConfig(): Promise<PaymentReminderConfig> {
    const response = await fetch(
      `${this.baseUrl}/system-config/payment-reminders`,
      {
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json'
        }
      }
    );

    if (!response.ok) {
      throw new Error('Failed to fetch config');
    }

    return response.json();
  }

  async updateConfig(config: PaymentReminderConfig): Promise<PaymentReminderConfig> {
    const response = await fetch(
      `${this.baseUrl}/system-config/payment-reminders`,
      {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(config)
      }
    );

    if (!response.ok) {
      throw new Error('Failed to update config');
    }

    return response.json();
  }
}

// Uso
const service = new PaymentReminderService(API_BASE_URL, token);
const config = await service.getConfig();
const updated = await service.updateConfig({
  payment_reminder_interval_days: 5,
  payment_reminder_check_interval_hours: 12
});
```

---

## 📱 Integración en el Menú

Agregar en el menú de configuración del superadmin:

```jsx
{user.role === 'SUPERADMIN' && (
  <NavItem to="/settings/payment-reminders">
    Recordatorios de Pago
  </NavItem>
)}
```

---

## ⚡ Características Importantes

1. **Actualización en Tiempo Real**: El scheduler se reinicia automáticamente
2. **Validación**: Los valores se validan tanto en frontend como backend
3. **Persistencia**: Los valores se guardan en base de datos
4. **Retrocompatibilidad**: Si no hay valores en BD, usa los del `.env`

---

## 🐛 Manejo de Errores

```jsx
const handleError = (error) => {
  if (error.status === 401) {
    // Token expirado, redirigir a login
    redirectToLogin();
  } else if (error.status === 403) {
    // No es superadmin
    showMessage('No tienes permisos para esta acción');
  } else if (error.status === 422) {
    // Validación fallida
    showMessage('Valores fuera del rango permitido');
  } else {
    // Error genérico
    showMessage('Error al guardar configuración');
  }
};
```

---

## 📞 Soporte

Si tienes dudas sobre la implementación:
1. Revisa `PAYMENT_REMINDERS_CONFIG.md` para documentación completa de la API
2. Ejecuta `test_payment_config.py` para probar los endpoints
3. Verifica los logs del servidor para debugging

---

## ✅ Checklist de Implementación

- [ ] Crear componente `PaymentReminderSettings`
- [ ] Agregar estilos CSS
- [ ] Proteger ruta (solo SUPERADMIN)
- [ ] Integrar en el menú de configuración
- [ ] Implementar manejo de errores
- [ ] Agregar validaciones de formulario
- [ ] Probar con usuario SUPERADMIN
- [ ] Probar con usuario no-SUPERADMIN (debe denegar acceso)
- [ ] Verificar que los cambios se reflejen en el sistema
