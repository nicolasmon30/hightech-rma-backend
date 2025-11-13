from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Configuración según el tipo de base de datos
if settings.is_sqlite:
    # SQLite requiere check_same_thread=False para FastAPI
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL no necesita configuración especial
    engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependency para obtener sesión de base de datos
    Se usa en los endpoints de FastAPI
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Crear todas las tablas"""
    Base.metadata.create_all(bind=engine)