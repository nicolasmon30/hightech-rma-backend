from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.country import Country
from app.models.user import User, UserRole, LanguageCode
from app.core.security import get_password_hash


def init_data():
    """
    Crear datos iniciales (países y superadmin)
    """
    db = SessionLocal()
    
    try:
        # Verificar si ya existen datos
        existing_countries = db.query(Country).count()
        if existing_countries > 0:
            print("⚠️  Ya existen datos en la base de datos")
            return
        
        # Crear países
        print("📍 Creando países...")
        usa = Country(name="United States", code="US", is_active=True)
        colombia = Country(name="Colombia", code="CO", is_active=True)
        
        db.add(usa)
        db.add(colombia)
        db.commit()
        db.refresh(usa)
        db.refresh(colombia)
        print("✅ Países creados: USA, Colombia")
        
        # Crear superadmin
        print("👤 Creando superadmin...")
        superadmin = User(
            email="admin@hightech.com",
            hashed_password=get_password_hash("Admin123!"),
            full_name="Super Admin",
            phone="+1234567890",
            company="HighTech Supplies",
            role=UserRole.SUPERADMIN,
            language=LanguageCode.EN,
            is_active=True,
            is_verified=True
        )
        superadmin.countries = [usa, colombia]
        
        db.add(superadmin)
        db.commit()
        print("✅ Superadmin creado")
        print("   Email: admin@hightech.com")
        print("   Password: Admin123!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Inicializando datos...")
    init_data()
    print("✅ Proceso completado")