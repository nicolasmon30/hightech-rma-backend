"""
Script para crear el superadmin inicial en Railway/producción.
Ejecutar después de las migraciones con: python init_superadmin.py
"""
import sys
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole, LanguageCode
from app.models.country import Country


def create_superadmin():
    """Crea el superadmin si no existe"""
    db: Session = SessionLocal()
    
    try:
        # Email del superadmin
        SUPERADMIN_EMAIL = "nmonroy97@gmail.com"
        SUPERADMIN_PASSWORD = "Admin2024!"  # ⚠️ CAMBIAR INMEDIATAMENTE DESPUÉS DEL PRIMER LOGIN
        
        # Verificar si ya existe
        existing = db.query(User).filter(User.email == SUPERADMIN_EMAIL).first()
        if existing:
            print(f"✅ Superadmin ya existe: {existing.email}")
            return
        
        # Obtener o crear país por defecto
        country = db.query(Country).first()
        if not country:
            print("⚠️  No hay países, creando país por defecto...")
            country = Country(
                name="United States",
                code="US",
                is_active=True
            )
            db.add(country)
            db.commit()
            db.refresh(country)
        
        # Crear superadmin
        superadmin = User(
            email=SUPERADMIN_EMAIL,
            hashed_password=get_password_hash(SUPERADMIN_PASSWORD),
            full_name="Nicolas Monroy",
            phone=None,
            company="HighTech Supplies",
            role=UserRole.SUPERADMIN,
            language=LanguageCode.ES,
            is_active=True,
            is_verified=True
        )
        
        # Asignar país
        superadmin.countries = [country]
        
        db.add(superadmin)
        db.commit()
        db.refresh(superadmin)
        
        print("=" * 60)
        print("✅ SUPERADMIN CREADO EXITOSAMENTE")
        print("=" * 60)
        print(f"Email:    {superadmin.email}")
        print(f"Password: {SUPERADMIN_PASSWORD}")
        print(f"Rol:      {superadmin.role}")
        print("=" * 60)
        print("⚠️  IMPORTANTE: Cambia la contraseña inmediatamente después")
        print("   del primer login en el sistema.")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error creando superadmin: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Inicializando superadmin...")
    create_superadmin()
    print("✅ Proceso completado")
