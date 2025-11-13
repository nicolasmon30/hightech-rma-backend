from app.core.database import engine
from app.models import Base


def init_db():
    """
    Crea todas las tablas en la base de datos
    """
    print("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas exitosamente")


if __name__ == "__main__":
    init_db()