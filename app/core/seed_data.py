"""
Script para poblar la base de datos con datos de prueba
Ejecutar: python -m app.core.seed_data
"""
from datetime import datetime  # ✅ Cambiado
import random  # ✅ Cambiado
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.country import Country
from app.models.user import User, UserRole, LanguageCode
from app.models.brand import Brand
from app.models.product import Product
from app.models.model import Model
from app.models.rma import RMA, RMAStatus
from app.models.rma_item import RMAItem, ServiceType
from app.core.security import get_password_hash


def clear_database(db: Session):
    """Limpiar toda la base de datos"""
    print("🗑️  Limpiando base de datos...")
    
    # 1. Eliminar RMAs (esto eliminará el historial automáticamente por cascade)
    db.query(RMA).delete()
    db.commit()
    
    # 2. Eliminar modelos y productos
    db.query(Model).delete()
    db.query(Product).delete()
    db.commit()
    
    # 3. Limpiar relaciones de marcas
    brands = db.query(Brand).all()
    for brand in brands:
        brand.countries.clear()
    db.commit()
    
    # 4. Eliminar marcas
    db.query(Brand).delete()
    db.commit()
    
    # 5. Limpiar relaciones de usuarios
    users = db.query(User).all()
    for user in users:
        user.countries.clear()
    db.commit()
    
    # 6. Eliminar usuarios
    db.query(User).delete()
    db.commit()
    
    # 7. Eliminar países
    db.query(Country).delete()
    db.commit()
    
    print("✅ Base de datos limpiada")


def create_countries(db: Session) -> dict:
    """Crear países"""
    print("\n📍 Creando países...")
    
    usa = Country(name="United States", code="US", is_active=True)
    colombia = Country(name="Colombia", code="CO", is_active=True)
    mexico = Country(name="Mexico", code="MX", is_active=True)
    
    db.add_all([usa, colombia, mexico])
    db.commit()
    
    db.refresh(usa)
    db.refresh(colombia)
    db.refresh(mexico)
    
    print(f"✅ Países creados: {usa.name}, {colombia.name}, {mexico.name}")
    
    return {
        "usa": usa,
        "colombia": colombia,
        "mexico": mexico
    }


def create_users(db: Session, countries: dict) -> dict:
    """Crear usuarios de prueba"""
    print("\n👥 Creando usuarios...")
    
    # SUPERADMIN - Acceso a todos los países
    superadmin = User(
        email="superadmin@hightech.com",
        hashed_password=get_password_hash("Super123!"),
        full_name="Super Admin",
        phone="+1234567890",
        company="HighTech Supplies HQ",
        role=UserRole.SUPERADMIN,
        language=LanguageCode.EN,
        is_active=True,
        is_verified=True
    )
    db.add(superadmin)
    db.commit()
    db.refresh(superadmin)
    superadmin.countries = [countries["usa"], countries["colombia"], countries["mexico"]]
    db.commit()
    
    # ADMIN USA - Solo USA
    admin_usa = User(
        email="admin.usa@hightech.com",
        hashed_password=get_password_hash("Admin123!"),
        full_name="Admin USA",
        phone="+1987654321",
        company="HighTech USA",
        role=UserRole.ADMIN,
        language=LanguageCode.EN,
        is_active=True,
        is_verified=True
    )
    db.add(admin_usa)
    db.commit()
    db.refresh(admin_usa)
    admin_usa.countries = [countries["usa"]]
    db.commit()
    
    # ADMIN Colombia - Solo Colombia
    admin_co = User(
        email="admin.co@hightech.com",
        hashed_password=get_password_hash("Admin123!"),
        full_name="Admin Colombia",
        phone="+57300123456",
        company="HighTech Colombia",
        role=UserRole.ADMIN,
        language=LanguageCode.ES,
        is_active=True,
        is_verified=True
    )
    db.add(admin_co)
    db.commit()
    db.refresh(admin_co)
    admin_co.countries = [countries["colombia"]]
    db.commit()
    
    # USER USA
    user_usa = User(
        email="user.usa@example.com",
        hashed_password=get_password_hash("User123!"),
        full_name="John Doe",
        phone="+1555123456",
        company="Tech Corp USA",
        role=UserRole.USER,
        language=LanguageCode.EN,
        is_active=True,
        is_verified=True
    )
    db.add(user_usa)
    db.commit()
    db.refresh(user_usa)
    user_usa.countries = [countries["usa"]]
    db.commit()
    
    # USER Colombia
    user_co = User(
        email="user.co@example.com",
        hashed_password=get_password_hash("User123!"),
        full_name="Juan Pérez",
        phone="+57300987654",
        company="Empresa Colombia",
        role=UserRole.USER,
        language=LanguageCode.ES,
        is_active=True,
        is_verified=True
    )
    db.add(user_co)
    db.commit()
    db.refresh(user_co)
    user_co.countries = [countries["colombia"]]
    db.commit()
    
    print("✅ Usuarios creados:")
    print(f"   - SUPERADMIN: superadmin@hightech.com / Super123!")
    print(f"   - ADMIN USA: admin.usa@hightech.com / Admin123!")
    print(f"   - ADMIN CO: admin.co@hightech.com / Admin123!")
    print(f"   - USER USA: user.usa@example.com / User123!")
    print(f"   - USER CO: user.co@example.com / User123!")
    
    return {
        "superadmin": superadmin,
        "admin_usa": admin_usa,
        "admin_co": admin_co,
        "user_usa": user_usa,
        "user_co": user_co
    }


def create_brands(db: Session, countries: dict) -> dict:
    """Crear marcas"""
    print("\n🏷️  Creando marcas...")
    
    # Dell - USA y Colombia
    dell = Brand(name="Dell", is_active=True)
    db.add(dell)
    db.commit()
    db.refresh(dell)
    dell.countries = [countries["usa"], countries["colombia"]]
    db.commit()
    
    # HP - Todos los países
    hp = Brand(name="HP", is_active=True)
    db.add(hp)
    db.commit()
    db.refresh(hp)
    hp.countries = [countries["usa"], countries["colombia"], countries["mexico"]]
    db.commit()
    
    # Lenovo - USA y Colombia
    lenovo = Brand(name="Lenovo", is_active=True)
    db.add(lenovo)
    db.commit()
    db.refresh(lenovo)
    lenovo.countries = [countries["usa"], countries["colombia"]]  # ✅ Agregado Colombia
    db.commit()
    
    print(f"✅ Marcas creadas: {dell.name}, {hp.name}, {lenovo.name}")
    
    return {
        "dell": dell,
        "hp": hp,
        "lenovo": lenovo
    }


def create_products(db: Session, brands: dict) -> dict:
    """Crear productos"""
    print("\n📦 Creando productos...")
    
    products = {}
    
    # Productos Dell
    dell_laptop = Product(name="Laptop", brand_id=brands["dell"].id, is_active=True)
    dell_desktop = Product(name="Desktop", brand_id=brands["dell"].id, is_active=True)
    db.add_all([dell_laptop, dell_desktop])
    
    # Productos HP
    hp_laptop = Product(name="Laptop", brand_id=brands["hp"].id, is_active=True)
    hp_printer = Product(name="Printer", brand_id=brands["hp"].id, is_active=True)
    db.add_all([hp_laptop, hp_printer])
    
    # Productos Lenovo
    lenovo_laptop = Product(name="ThinkPad", brand_id=brands["lenovo"].id, is_active=True)
    db.add(lenovo_laptop)
    
    db.commit()
    
    db.refresh(dell_laptop)
    db.refresh(dell_desktop)
    db.refresh(hp_laptop)
    db.refresh(hp_printer)
    db.refresh(lenovo_laptop)
    
    products = {
        "dell_laptop": dell_laptop,
        "dell_desktop": dell_desktop,
        "hp_laptop": hp_laptop,
        "hp_printer": hp_printer,
        "lenovo_laptop": lenovo_laptop
    }
    
    print(f"✅ {len(products)} productos creados")
    
    return products


def create_models(db: Session, products: dict) -> dict:
    """Crear modelos"""
    print("\n🔧 Creando modelos...")
    
    models = {}
    
    # Modelos Dell Laptop
    dell_xps13 = Model(name="XPS 13", product_id=products["dell_laptop"].id, is_active=True)
    dell_xps15 = Model(name="XPS 15", product_id=products["dell_laptop"].id, is_active=True)
    dell_latitude = Model(name="Latitude 5420", product_id=products["dell_laptop"].id, is_active=True)
    
    # Modelos Dell Desktop
    dell_optiplex = Model(name="OptiPlex 7090", product_id=products["dell_desktop"].id, is_active=True)
    
    # Modelos HP Laptop
    hp_elitebook = Model(name="EliteBook 840", product_id=products["hp_laptop"].id, is_active=True)
    hp_pavilion = Model(name="Pavilion 15", product_id=products["hp_laptop"].id, is_active=True)
    
    # Modelos HP Printer
    hp_laserjet = Model(name="LaserJet Pro M404", product_id=products["hp_printer"].id, is_active=True)
    
    # Modelos Lenovo
    lenovo_x1 = Model(name="X1 Carbon Gen 9", product_id=products["lenovo_laptop"].id, is_active=True)
    lenovo_t14 = Model(name="T14 Gen 2", product_id=products["lenovo_laptop"].id, is_active=True)
    
    db.add_all([
        dell_xps13, dell_xps15, dell_latitude, dell_optiplex,
        hp_elitebook, hp_pavilion, hp_laserjet,
        lenovo_x1, lenovo_t14
    ])
    
    db.commit()
    
    for model in [dell_xps13, dell_xps15, dell_latitude, dell_optiplex,
                  hp_elitebook, hp_pavilion, hp_laserjet, lenovo_x1, lenovo_t14]:
        db.refresh(model)
    
    models = {
        "dell_xps13": dell_xps13,
        "dell_xps15": dell_xps15,
        "dell_latitude": dell_latitude,
        "dell_optiplex": dell_optiplex,
        "hp_elitebook": hp_elitebook,
        "hp_pavilion": hp_pavilion,
        "hp_laserjet": hp_laserjet,
        "lenovo_x1": lenovo_x1,
        "lenovo_t14": lenovo_t14
    }
    
    print(f"✅ {len(models)} modelos creados")
    
    return models


def create_rmas(db: Session, users: dict, countries: dict, brands: dict, products: dict, models: dict):
    """Crear RMAs de prueba"""
    print("\n📋 Creando RMAs de prueba...")
    
    from app.crud import rma as crud_rma
    from app.schemas.rma import RMACreate, RMAItemCreate
    
    # RMA 1: USA - Dell Laptop con 2 items
    rma1_data = RMACreate(
        company_name="Tech Corp USA",
        company_address="123 Main St, New York, NY",
        postal_code="10001",
        items=[
            RMAItemCreate(
                brand_id=brands["dell"].id,
                product_id=products["dell_laptop"].id,
                model_id=models["dell_xps13"].id,
                serial_number="DLL001XPS13A",
                service_type=ServiceType.CALIBRATION,
                issue_description="Laptop no enciende. Se presiona el botón de power y no responde. LED de carga funciona correctamente."
            ),
            RMAItemCreate(
                brand_id=brands["dell"].id,
                product_id=products["dell_laptop"].id,
                model_id=models["dell_xps15"].id,
                serial_number="DLL002XPS15B",
                service_type=ServiceType.REPAIR,
                issue_description="Pantalla rota después de caída."
            )
        ]
    )
    
    rma1 = crud_rma.create_with_user(
        db=db,
        obj_in=rma1_data,
        user_id=users["user_usa"].id,
        country_id=countries["usa"].id
    )
    
    # RMA 2: Colombia - HP Laptop
    rma2_data = RMACreate(
        company_name="Empresa Colombia",
        company_address="Calle 100 # 20-30, Bogotá",
        postal_code="110111",
        items=[
            RMAItemCreate(
                brand_id=brands["hp"].id,
                product_id=products["hp_laptop"].id,
                model_id=models["hp_elitebook"].id,
                serial_number="HP001ELITE840",
                service_type=ServiceType.BOTH,
                issue_description="Pantalla con líneas verticales. Problema comenzó después de caída."
            )
        ]
    )
    
    rma2 = crud_rma.create_with_user(
        db=db,
        obj_in=rma2_data,
        user_id=users["user_co"].id,
        country_id=countries["colombia"].id
    )
    
    # RMA 3: USA - HP Printer
    rma3_data = RMACreate(
        company_name="Office Solutions LLC",
        company_address="456 Business Ave, Los Angeles, CA",
        postal_code="90001",
        items=[
            RMAItemCreate(
                brand_id=brands["hp"].id,
                product_id=products["hp_printer"].id,
                model_id=models["hp_laserjet"].id,
                serial_number="HP002LJ404PRO",
                service_type=ServiceType.CALIBRATION,
                issue_description="Impresora no imprime. Muestra error de papel atascado pero no hay papel."
            )
        ]
    )
    
    rma3 = crud_rma.create_with_user(
        db=db,
        obj_in=rma3_data,
        user_id=users["user_usa"].id,
        country_id=countries["usa"].id
    )
    
    # Actualizar estado del RMA 3 a APPROVED
    crud_rma.update_status(
        db=db,
        rma=rma3,
        new_status=RMAStatus.APPROVED,
        user_id=users["admin_usa"].id,
        comment="RMA aprobado. Proceder con reparación."
    )
    
    # RMA 4: Colombia - Dell Desktop + Lenovo
    rma4_data = RMACreate(
        company_name="Sistemas Integrales SAS",
        company_address="Carrera 7 # 80-45, Medellín",
        postal_code="050001",
        items=[
            RMAItemCreate(
                brand_id=brands["dell"].id,
                product_id=products["dell_desktop"].id,
                model_id=models["dell_optiplex"].id,
                serial_number="DLL002OPT7090",
                service_type=ServiceType.REPAIR,
                issue_description="Computador se reinicia aleatoriamente. Problema persiste después de reinstalar sistema operativo."
            ),
            RMAItemCreate(
                brand_id=brands["lenovo"].id,
                product_id=products["lenovo_laptop"].id,
                model_id=models["lenovo_x1"].id,
                serial_number="LEN001X1CARB",
                service_type=ServiceType.CALIBRATION,
                issue_description="Batería no carga más del 50%."
            )
        ]
    )
    
    rma4 = crud_rma.create_with_user(
        db=db,
        obj_in=rma4_data,
        user_id=users["user_co"].id,
        country_id=countries["colombia"].id
    )
    
    print(f"✅ RMAs creados:")
    print(f"   - {rma1.rma_number} (USA - 2 items Dell Laptop)")
    print(f"   - {rma2.rma_number} (Colombia - HP Laptop)")
    print(f"   - {rma3.rma_number} (USA - HP Printer - APPROVED)")
    print(f"   - {rma4.rma_number} (Colombia - 2 items: Dell Desktop + Lenovo)")
    
    rmas_data = [
        {
            "user": users["user_usa"],
            "country": countries["usa"],
            "company_name": "Tech Solutions Miami",
            "company_address": "123 Biscayne Blvd, Miami, FL 33132",
            "postal_code": "33132",
            "status": RMAStatus.RMA_SUBMITTED,
            "items": [
                {
                    "brand": brands["dell"],
                    "product": products["dell_laptop"],
                    "model": models["dell_xps13"],  # ✅ Corregido
                    "serial_number": "DELL-XPS13-001",
                    "service_type": ServiceType.CALIBRATION,
                    "issue_description": "La pantalla no enciende. El LED de power parpadea 3 veces."
                },
                {
                    "brand": brands["dell"],
                    "product": products["dell_laptop"],
                    "model": models["dell_latitude"],  # ✅ Corregido
                    "serial_number": "DELL-LAT-002",
                    "service_type": ServiceType.BOTH,
                    "issue_description": "Teclado no responde después de derrame de líquido."
                }
            ]
        },
        {
            "user": users["user_usa"],
            "country": countries["usa"],
            "company_name": "Miami Business Center",
            "company_address": "456 Ocean Drive, Miami, FL 33139",
            "postal_code": "33139",
            "status": RMAStatus.APPROVED,
            "items": [
                {
                    "brand": brands["hp"],
                    "product": products["hp_laptop"],
                    "model": models["hp_elitebook"],  # ✅ Corregido
                    "serial_number": "HP-ELITE-003",
                    "service_type": ServiceType.REPAIR,
                    "issue_description": "Batería no carga, se apaga constantemente."
                }
            ]
        },
        {
            "user": users["user_co"],
            "country": countries["colombia"],
            "company_name": "Soluciones Tech Bogotá",
            "company_address": "Cra 7 #32-16, Bogotá",
            "postal_code": "110311",
            "status": RMAStatus.EVALUATING,
            "items": [
                {
                    "brand": brands["lenovo"],
                    "product": products["lenovo_laptop"],
                    "model": models["lenovo_x1"],  # ✅ Corregido
                    "serial_number": "LENOVO-X1-004",
                    "service_type": ServiceType.CALIBRATION,
                    "issue_description": "Pantalla con líneas verticales, posible daño en cable."
                },
                {
                    "brand": brands["hp"],
                    "product": products["hp_printer"],
                    "model": models["hp_laserjet"],  # ✅ Corregido
                    "serial_number": "HP-LASER-005",
                    "service_type": ServiceType.BOTH,
                    "issue_description": "Atasco de papel constante, rodillos dañados."
                }
            ]
        }
    ]
    
    created_rmas = []
    
    for rma_data in rmas_data:
        # Solo generar rma_number si el estado es APPROVED
        rma_number = None
        if rma_data["status"] == RMAStatus.APPROVED:
            rma_number = f"RMA-{datetime.utcnow().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        
        rma = RMA(
            rma_number=rma_number,
            company_name=rma_data["company_name"],
            company_address=rma_data["company_address"],
            postal_code=rma_data["postal_code"],
            status=rma_data["status"],
            country_id=rma_data["country"].id,
            created_by=rma_data["user"].id
        )
        db.add(rma)
        db.flush()
        
        for item_data in rma_data["items"]:
            rma_item = RMAItem(
                rma_id=rma.id,
                brand_id=item_data["brand"].id,
                product_id=item_data["product"].id,
                model_id=item_data["model"].id,
                serial_number=item_data["serial_number"],
                service_type=item_data["service_type"],
                issue_description=item_data["issue_description"]
            )
            db.add(rma_item)
        
        created_rmas.append(rma)
    
    db.commit()
    
    print(f"✅ RMAs creados: {len(created_rmas)}")
    for rma in created_rmas:
        rma_num = rma.rma_number if rma.rma_number else "SIN NÚMERO (pendiente aprobación)"
        print(f"   - {rma_num}: {len(rma.items)} items - Estado: {rma.status.value}")
    
    return created_rmas


def seed_all():
    """Ejecutar todo el proceso de seeding"""
    db = SessionLocal()
    
    try:
        print("🌱 Iniciando seeding de base de datos...")
        print("=" * 60)
        
        # Limpiar base de datos
        clear_database(db)
        
        # Crear datos
        countries = create_countries(db)
        users = create_users(db, countries)
        brands = create_brands(db, countries)
        products = create_products(db, brands)
        models = create_models(db, products)
        create_rmas(db, users, countries, brands, products, models)  # ✅ Cambiado de seed_rmas a create_rmas
        
        print("\n" + "=" * 60)
        print("✅ Seeding completado exitosamente!")
        print("\n📝 CREDENCIALES DE PRUEBA:")
        print("-" * 60)
        print("SUPERADMIN:")
        print("  Email: superadmin@hightech.com")
        print("  Password: Super123!")
        print()
        print("ADMIN USA:")
        print("  Email: admin.usa@hightech.com")
        print("  Password: Admin123!")
        print()
        print("ADMIN COLOMBIA:")
        print("  Email: admin.co@hightech.com")
        print("  Password: Admin123!")
        print()
        print("USER USA:")
        print("  Email: user.usa@example.com")
        print("  Password: User123!")
        print()
        print("USER COLOMBIA:")
        print("  Email: user.co@example.com")
        print("  Password: User123!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error durante el seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_all()