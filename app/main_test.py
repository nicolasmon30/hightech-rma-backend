"""
⚠️ MAIN DE TESTING - SOLO DESARROLLO ⚠️
Versión del main.py que usa el scheduler de testing con segundos
NO USAR EN PRODUCCIÓN

Para ejecutar:
uvicorn app.main_test:app --reload --port 8001
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.api.v1.router import api_router

# ⚡ IMPORTAR SCHEDULER DE TESTING (no el normal)
from app.services.scheduler_service_test import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestión del ciclo de vida de la aplicación
    Startup: Iniciar scheduler de recordatorios EN MODO TESTING
    Shutdown: Detener scheduler
    """
    # Startup
    print("🚀 Iniciando HighTech RMA System [TESTING MODE]...")
    print("⚡ Recordatorios configurados para SEGUNDOS (no días)")
    start_scheduler()
    
    yield
    
    # Shutdown
    print("🛑 Apagando HighTech RMA System [TESTING MODE]...")
    stop_scheduler()


# Crear instancia de FastAPI
app = FastAPI(
    title=f"{settings.PROJECT_NAME} [TESTING]",
    version=settings.VERSION,
    description="Sistema de gestión de RMA - MODO TESTING CON RECORDATORIOS CADA 3 SEGUNDOS",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "message": "HighTech RMA System API [TESTING MODE]",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": f"{settings.API_V1_STR}/docs",
        "warning": "⚠️ Scheduler en modo testing: recordatorios cada 3 segundos"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "mode": "TESTING - Recordatorios cada 3 segundos"
    }
