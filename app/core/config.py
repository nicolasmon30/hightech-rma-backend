from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Union


class Settings(BaseSettings):
    """
    Configuración general de la aplicación.
    Lee las variables desde el archivo .env
    """
    
    # Información del proyecto
    PROJECT_NAME: str
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Seguridad
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 30 minutos
    
    # Base de datos
    DATABASE_URL: str = "sqlite:///./hightech_rma.db"
    
    # CORS (permitir frontend)
    BACKEND_CORS_ORIGINS: Union[List[str], str] = []
    
    @field_validator('BACKEND_CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parsear BACKEND_CORS_ORIGINS desde string separado por comas"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    # Frontend URL (para links en emails)
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Resend (Emails)
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "noreply@hightech.com"
    EMAIL_ENABLED: bool = False
    
    # Internacionalización
    SUPPORTED_LANGUAGES: Union[List[str], str] = ["en", "es"]
    DEFAULT_LANGUAGE: str = "en"
    
    @field_validator('SUPPORTED_LANGUAGES', mode='before')
    @classmethod
    def parse_supported_languages(cls, v):
        """Parsear SUPPORTED_LANGUAGES desde string separado por comas"""
        if isinstance(v, str):
            return [lang.strip() for lang in v.split(",") if lang.strip()]
        return v
    
    # Paginación
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # MinIO/Storage
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ROOT_USER: str = "minioadmin"
    MINIO_ROOT_PASSWORD: str = "minioadmin"
    MINIO_SECURE: bool = False
    MINIO_BUCKET_NAME: str = "development-rma-documents"

    # File Upload
    MAX_FILE_SIZE_MB: int = 2
    ALLOWED_EXTENSIONS: str = ".pdf"
    FILE_RETENTION_DAYS: int = 60
    
    # Payment Reminders Scheduler
    PAYMENT_REMINDER_INTERVAL_DAYS: int = 3  # Días entre recordatorios
    PAYMENT_REMINDER_CHECK_INTERVAL_HOURS: int = 24  # Frecuencia de verificación del scheduler


    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )
    
    @property
    def max_file_size_bytes(self) -> int:
        """Convierte MB a bytes"""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """Convierte string de extensiones a lista"""
        if isinstance(self.ALLOWED_EXTENSIONS, list):
            return self.ALLOWED_EXTENSIONS
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Retorna lista de orígenes CORS (ya parseada por el validator)"""
        if isinstance(self.BACKEND_CORS_ORIGINS, list):
            return self.BACKEND_CORS_ORIGINS
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]
    
    @property
    def is_sqlite(self) -> bool:
        """Detecta si la BD es SQLite"""
        return self.DATABASE_URL.startswith("sqlite")
    
    @property
    def is_production(self) -> bool:
        """Detecta si está en producción"""
        return self.ENVIRONMENT == "production"


# Instancia global de configuración
settings = Settings()