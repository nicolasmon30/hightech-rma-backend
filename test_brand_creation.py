"""
Script para probar la creación de brands con description
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.brand import Brand
from app.models.country import Country

def test_brand():
    db: Session = SessionLocal()
    
    try:
        # Verificar que existe el campo description
        print("🔍 Verificando estructura de Brand...")
        
        # Intentar crear una brand de prueba
        print("\n📝 Creando brand de prueba...")
        
        # Buscar un país existente
        country = db.query(Country).first()
        if not country:
            print("❌ No hay países en la base de datos")
            return
        
        print(f"✅ País encontrado: {country.name}")
        
        # Crear brand
        test_brand = Brand(
            name="Test Brand " + str(hash("test")),
            description="Esta es una descripción de prueba",
            is_active=True
        )
        test_brand.countries = [country]
        
        db.add(test_brand)
        db.commit()
        db.refresh(test_brand)
        
        print(f"\n✅ Brand creada exitosamente:")
        print(f"   ID: {test_brand.id}")
        print(f"   Nombre: {test_brand.name}")
        print(f"   Descripción: {test_brand.description}")
        print(f"   Países: {[c.name for c in test_brand.countries]}")
        
        # Limpiar
        db.delete(test_brand)
        db.commit()
        print(f"\n🗑️  Brand de prueba eliminada")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_brand()
