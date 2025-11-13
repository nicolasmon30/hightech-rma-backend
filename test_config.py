"""
Script para verificar que la configuración se carga correctamente
"""
from app.core.config import settings

print("=" * 60)
print("🔧 VERIFICACIÓN DE CONFIGURACIÓN")
print("=" * 60)

print(f"\n📋 Información del Proyecto:")
print(f"   Nombre: {settings.PROJECT_NAME}")
print(f"   Versión: {settings.VERSION}")
print(f"   Entorno: {settings.ENVIRONMENT}")

print(f"\n🔐 Seguridad:")
print(f"   Algorithm: {settings.ALGORITHM}")
print(f"   Token Expiry: {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutos")

print(f"\n🗄️  Base de Datos:")
print(f"   URL: {settings.DATABASE_URL}")

print(f"\n🌍 CORS Origins:")
print(f"   Tipo: {type(settings.BACKEND_CORS_ORIGINS)}")
print(f"   Cantidad: {len(settings.BACKEND_CORS_ORIGINS)}")
for i, origin in enumerate(settings.BACKEND_CORS_ORIGINS, 1):
    print(f"   {i}. {origin}")

print(f"\n🌐 Frontend:")
print(f"   URL: {settings.FRONTEND_URL}")

print(f"\n📧 Email:")
print(f"   Habilitado: {settings.EMAIL_ENABLED}")
print(f"   From: {settings.EMAIL_FROM}")

print(f"\n🗣️  Idiomas:")
print(f"   Soportados: {settings.SUPPORTED_LANGUAGES}")
print(f"   Por defecto: {settings.DEFAULT_LANGUAGE}")

print(f"\n📦 MinIO:")
print(f"   Endpoint: {settings.MINIO_ENDPOINT}")
print(f"   Bucket: {settings.MINIO_BUCKET_NAME}")

print(f"\n📄 File Upload:")
print(f"   Max Size: {settings.MAX_FILE_SIZE_MB} MB")
print(f"   Extensions: {settings.ALLOWED_EXTENSIONS}")

print("\n" + "=" * 60)
print("✅ Configuración cargada exitosamente")
print("=" * 60)
