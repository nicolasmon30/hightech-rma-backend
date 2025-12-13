# Configuración de Recordatorios de Pago

## Descripción
Sistema de configuración dinámica para gestionar los parámetros de recordatorios de pago desde el frontend. Solo accesible para usuarios con rol **SUPERADMIN**.

## Funcionalidades Implementadas

### 1. Modelo de Base de Datos
- **Tabla**: `system_config`
- **Campos**:
  - `id`: Identificador único
  - `key`: Clave de configuración (única)
  - `value`: Valor de la configuración
  - `description`: Descripción de la configuración
  - `created_at`: Fecha de creación
  - `updated_at`: Fecha de última actualización

### 2. Endpoints API (Solo SUPERADMIN)

#### Obtener configuración actual de recordatorios
```http
GET /api/v1/system-config/payment-reminders
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "payment_reminder_interval_days": 3,
  "payment_reminder_check_interval_hours": 24
}
```

#### Actualizar configuración de recordatorios
```http
PUT /api/v1/system-config/payment-reminders
Authorization: Bearer {token}
Content-Type: application/json

{
  "payment_reminder_interval_days": 5,
  "payment_reminder_check_interval_hours": 12
}
```

**Parámetros:**
- `payment_reminder_interval_days`: Días entre recordatorios (1-30)
- `payment_reminder_check_interval_hours`: Frecuencia de verificación en horas (1-168)

**Nota**: El scheduler se reinicia automáticamente al actualizar la configuración.

#### Obtener todas las configuraciones del sistema
```http
GET /api/v1/system-config/
Authorization: Bearer {token}
```

#### Obtener configuración específica por clave
```http
GET /api/v1/system-config/{key}
Authorization: Bearer {token}
```

#### Crear nueva configuración
```http
POST /api/v1/system-config/
Authorization: Bearer {token}
Content-Type: application/json

{
  "key": "NUEVA_CONFIGURACION",
  "value": "valor",
  "description": "Descripción de la configuración"
}
```

#### Actualizar configuración existente
```http
PUT /api/v1/system-config/{key}
Authorization: Bearer {token}
Content-Type: application/json

{
  "value": "nuevo_valor"
}
```

#### Eliminar configuración
```http
DELETE /api/v1/system-config/{key}
Authorization: Bearer {token}
```

## Comportamiento del Sistema

### Valores por Defecto
Si no existen configuraciones en la base de datos, el sistema utiliza los valores del archivo `.env`:
- `PAYMENT_REMINDER_INTERVAL_DAYS=3`
- `PAYMENT_REMINDER_CHECK_INTERVAL_HOURS=24`

### Actualización Dinámica
1. El superadministrador actualiza la configuración desde el frontend
2. Los valores se guardan en la tabla `system_config`
3. El scheduler se reinicia automáticamente
4. Los nuevos valores se aplican inmediatamente

### Persistencia
Las configuraciones se almacenan en la base de datos y persisten entre reinicios del servidor.

## Seguridad
- ✅ Solo usuarios con rol **SUPERADMIN** pueden acceder a estos endpoints
- ✅ Validación de rangos de valores:
  - Días: 1-30
  - Horas: 1-168 (1 semana máximo)
- ✅ Las configuraciones se guardan de forma segura en la base de datos

## Flujo de Uso

### Para el Frontend
1. **Obtener configuración actual:**
   ```javascript
   const response = await fetch('/api/v1/system-config/payment-reminders', {
     headers: { 'Authorization': `Bearer ${token}` }
   });
   const config = await response.json();
   // { payment_reminder_interval_days: 3, payment_reminder_check_interval_hours: 24 }
   ```

2. **Actualizar configuración:**
   ```javascript
   const response = await fetch('/api/v1/system-config/payment-reminders', {
     method: 'PUT',
     headers: {
       'Authorization': `Bearer ${token}`,
       'Content-Type': 'application/json'
     },
     body: JSON.stringify({
       payment_reminder_interval_days: 5,
       payment_reminder_check_interval_hours: 12
     })
   });
   const updated = await response.json();
   ```

## Archivos Modificados/Creados

### Nuevos Archivos
- `app/models/system_config.py` - Modelo de base de datos
- `app/schemas/system_config.py` - Schemas de validación
- `app/crud/crud_system_config.py` - Operaciones CRUD
- `app/api/v1/endpoints/system_config.py` - Endpoints API
- `alembic/versions/be89ee339157_add_system_config_table.py` - Migración

### Archivos Modificados
- `app/models/__init__.py` - Exportar nuevo modelo
- `app/schemas/__init__.py` - Exportar nuevos schemas
- `app/crud/__init__.py` - Exportar nuevo CRUD
- `app/api/v1/router.py` - Registrar nuevos endpoints
- `app/services/scheduler_service.py` - Usar configuraciones dinámicas

## Testing

### Probar endpoints con curl

```bash
# Login como superadmin
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=superadmin@example.com&password=yourpassword"

# Obtener configuración
curl -X GET "http://localhost:8000/api/v1/system-config/payment-reminders" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Actualizar configuración
curl -X PUT "http://localhost:8000/api/v1/system-config/payment-reminders" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"payment_reminder_interval_days": 5, "payment_reminder_check_interval_hours": 12}'
```

## Notas Importantes

1. **Reinicio del Scheduler**: Cuando se actualiza la configuración de recordatorios, el scheduler se reinicia automáticamente para aplicar los cambios inmediatamente.

2. **Valores Iniciales**: La primera vez que se accede al endpoint GET, se crean automáticamente los registros en la base de datos con los valores del archivo `.env`.

3. **Compatibilidad**: El sistema sigue siendo compatible con las variables de entorno. Si no hay configuración en BD, usa los valores del `.env`.

4. **Logs**: El sistema registra en consola cuando se inicia/reinicia el scheduler y cuando se envían recordatorios.
