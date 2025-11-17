# 🚀 Deployment en Railway

## Variables de entorno requeridas

Configura estas variables en el dashboard de Railway:

### 🔐 Seguridad
```bash
SECRET_KEY=<genera con: openssl rand -hex 32>
```

### 🗄️ Base de datos
```bash
# Railway la configura automáticamente si usas PostgreSQL de Railway
# DATABASE_URL se genera automáticamente
```

### 📧 Email (Resend)
```bash
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxxxxx
EMAIL_FROM=soporte@hightech-ndt.com
EMAIL_ENABLED=true
```

### 🌐 Frontend/CORS
```bash
BACKEND_CORS_ORIGINS=https://tu-frontend.com,https://www.tu-frontend.com
FRONTEND_URL=https://tu-frontend.com
```

### 💾 MinIO/Storage
```bash
MINIO_ENDPOINT=tu-minio-endpoint.com
MINIO_ACCESS_KEY=tu-access-key
MINIO_SECRET_KEY=tu-secret-key
MINIO_SECURE=True
MINIO_BUCKET_NAME=production-rma-documents
```

### ⚙️ Configuración opcional
```bash
ENVIRONMENT=production
PROJECT_NAME=HighTech RMA System
VERSION=1.0.0
API_V1_STR=/api/v1
DEFAULT_LANGUAGE=es
PAYMENT_REMINDER_INTERVAL_DAYS=3
MAX_FILE_SIZE_MB=10
```

## 📋 Pasos para deploy

1. **Conecta tu repositorio a Railway**
2. **Agrega PostgreSQL** (desde Railway dashboard)
3. **Configura las variables de entorno** (ver arriba)
4. **Railway automáticamente:**
   - Ejecutará las migraciones (`alembic upgrade head`)
   - Creará el superadmin (`python init_superadmin.py`)
   - Iniciará el servidor

## 🔐 Credenciales del Superadmin

Después del primer deploy:
```
Email:    nmonroy97@gmail.com
Password: Admin2024!
```

**⚠️ IMPORTANTE:** Cambia la contraseña inmediatamente después del primer login.

## 🔍 Verificar deploy

Accede a: `https://tu-app.railway.app/api/v1/docs`

## 🐛 Troubleshooting

### Error: "Could not import module main"
- Verifica que `Procfile` tenga: `web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Verifica que `railway.json` tenga el `startCommand` correcto

### Error: Migraciones fallan
- Verifica que `DATABASE_URL` esté configurada
- Revisa los logs de Railway: `railway logs`

### Error: Email no funciona
- Verifica `RESEND_API_KEY` en las variables de entorno
- Verifica que el dominio esté verificado en Resend
