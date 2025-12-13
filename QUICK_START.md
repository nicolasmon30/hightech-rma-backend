# 🚀 Quick Start - Configuración de Recordatorios de Pago

## ✅ Estado Actual
- ✅ Migración aplicada (tabla `system_config` creada)
- ✅ Backend configurado y listo
- ✅ Endpoints funcionando

## 🔧 Comandos Útiles

### Iniciar el servidor
```bash
# En PowerShell
cd c:\Users\nicol\Documents\work-best\hightech-rma-backend
uvicorn app.main:app --reload
```

### Probar los endpoints

#### 1. Login como SUPERADMIN (PowerShell)
```powershell
$body = @{
    username = "superadmin@example.com"
    password = "tu_password"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"

$token = $response.access_token
```

#### 2. Obtener configuración actual
```powershell
$headers = @{
    "Authorization" = "Bearer $token"
}

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/system-config/payment-reminders" `
    -Headers $headers
```

#### 3. Actualizar configuración
```powershell
$config = @{
    payment_reminder_interval_days = 5
    payment_reminder_check_interval_hours = 12
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/system-config/payment-reminders" `
    -Method Put `
    -Headers $headers `
    -Body $config `
    -ContentType "application/json"
```

### Usar el script de prueba Python
```bash
# Editar test_payment_config.py y actualizar credenciales
# Luego ejecutar:
python test_payment_config.py
```

## 📋 Verificación

### Revisar logs del scheduler
Al iniciar el servidor, deberías ver:
```
🚀 Iniciando HighTech RMA System...
🕐 Scheduler iniciado: recordatorios cada 24h
```

### Verificar base de datos
```sql
-- Ver todas las configuraciones
SELECT * FROM system_config;

-- Ver configuraciones específicas
SELECT * FROM system_config 
WHERE key IN ('PAYMENT_REMINDER_INTERVAL_DAYS', 'PAYMENT_REMINDER_CHECK_INTERVAL_HOURS');
```

## 🎯 Endpoints Disponibles

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/system-config/payment-reminders` | Obtener config actual |
| PUT | `/api/v1/system-config/payment-reminders` | Actualizar config |
| GET | `/api/v1/system-config/` | Ver todas las configs |
| GET | `/api/v1/system-config/{key}` | Ver config específica |
| POST | `/api/v1/system-config/` | Crear nueva config |
| PUT | `/api/v1/system-config/{key}` | Actualizar por clave |
| DELETE | `/api/v1/system-config/{key}` | Eliminar config |

## 🔍 Swagger UI
Ver documentación interactiva:
```
http://localhost:8000/docs
```

Buscar la sección **"System Configuration"**

## 📝 Valores por Defecto

Si no hay configuración en BD, se usan estos valores del `.env`:
- `PAYMENT_REMINDER_INTERVAL_DAYS=3`
- `PAYMENT_REMINDER_CHECK_INTERVAL_HOURS=24`

## 🐛 Troubleshooting

### Error 403 Forbidden
- Verificar que el usuario es SUPERADMIN
- Verificar token JWT válido

### Error 422 Validation Error
- Días: debe estar entre 1-30
- Horas: debe estar entre 1-168

### Scheduler no se reinicia
- Verificar logs de consola
- Reiniciar servidor manualmente

## 📚 Documentación Completa

- **PAYMENT_REMINDERS_CONFIG.md** - Documentación técnica completa
- **FRONTEND_GUIDE.md** - Guía para implementar en frontend
- **IMPLEMENTATION_SUMMARY.md** - Resumen de la implementación

## 🎉 ¡Listo para Usar!

El backend está completamente funcional. Solo falta implementar la interfaz en el frontend siguiendo la guía en `FRONTEND_GUIDE.md`.
