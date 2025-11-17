"""Script de prueba para el endpoint público de tracking de RMA.
Ejecutar después de tener la BD inicializada.

Pasos:
1. Crea datos mínimos (Country, User, Brand, Product, Model)
2. Crea un RMA y lo aprueba (genera rma_number)
3. Llama al endpoint público /api/v1/public/rma/{rma_number}
4. Verifica respuesta y también prueba 404.
"""
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import SessionLocal
from app.models.country import Country
from app.models.user import User, UserRole, LanguageCode
from app.models.brand import Brand
from app.models.product import Product
from app.models.model import Model
from app.models.rma import RMAStatus
from app.crud import rma as crud_rma
from app.schemas.rma import RMACreate, RMAItemCreate
from uuid import uuid4


def create_minimum_data(db: Session):
    # Reutilizar país si ya existe, si no crear uno nuevo con código único
    country = db.query(Country).filter(Country.code == "TL").first()
    if not country:
        country = Country(name="Testland", code="TL", is_active=True)
        db.add(country)
        db.commit(); db.refresh(country)

    user = db.query(User).filter(User.email == "user@test.com").first()
    if not user:
        user = User(
            email="user@test.com",
            hashed_password="fakehashed",
            full_name="Test User",
            role=UserRole.USER,
            language=LanguageCode.ES,
            is_active=True,
            is_verified=True
        )
        user.countries = [country]
        db.add(user)
        db.commit(); db.refresh(user)
    elif country not in user.countries:
        user.countries.append(country)
        db.commit(); db.refresh(user)

    existing_brand = db.query(Brand).filter(Brand.name == "BrandX").first()
    brand = existing_brand or Brand(name="BrandX", description="Marca de prueba")
    if not existing_brand:
        db.add(brand)
        db.commit(); db.refresh(brand)
    if country not in brand.countries:
        brand.countries.append(country)
        db.commit(); db.refresh(brand)

    product = db.query(Product).filter(Product.name == "ProductoX", Product.brand_id == brand.id).first()
    if not product:
        product = Product(name="ProductoX", description="Prod de prueba", brand_id=brand.id)
        db.add(product)
        db.commit(); db.refresh(product)

    model = db.query(Model).filter(Model.name == "ModeloX", Model.product_id == product.id).first()
    if not model:
        model = Model(name="ModeloX", product_id=product.id)
        db.add(model)
        db.commit(); db.refresh(model)

    return country, user, brand, product, model


def create_and_approve_rma(db: Session, user: User, country: Country, product: Product, brand: Brand, model: Model):
    unique_serial = f"SN-DEMO-{uuid4().hex[:8]}"
    rma_in = RMACreate(
        company_name="Empresa Demo",
        company_address="Calle Falsa 123",
        postal_code="0001",
        items=[
            RMAItemCreate(
                brand_id=brand.id,
                product_id=product.id,
                model_id=model.id,
                serial_number=unique_serial,
                service_type="repair",
                issue_description="No enciende"
            )
        ]
    )
    rma_obj = crud_rma.create_with_user(db, obj_in=rma_in, user_id=user.id, country_id=country.id)

    # Aprobar (genera número)
    crud_rma.update_status(db, rma=rma_obj, new_status=RMAStatus.APPROVED, user_id=user.id, comment="Aprobado para seguimiento")
    db.refresh(rma_obj)
    return rma_obj


def test_public_tracking():
    db: Session = SessionLocal()
    try:
        country, user, brand, product, model = create_minimum_data(db)
        rma_obj = create_and_approve_rma(db, user, country, product, brand, model)
        assert rma_obj.rma_number, "El RMA debería tener número luego de aprobación"

        client = TestClient(app)

        # Llamar endpoint público
        url = f"/api/v1/public/rma/{rma_obj.rma_number}"
        resp = client.get(url)
        print(f"📡 GET {url} -> {resp.status_code}")
        assert resp.status_code == 200, f"Respuesta inesperada: {resp.text}"
        data = resp.json()
        print("✅ Datos recibidos:")
        print(data)

        # Validar campos clave
        assert data["rma_number"] == rma_obj.rma_number
        assert len(data["items"]) == 1
        assert len(data["history"]) >= 2  # Creación + aprobación

        # Probar RMA inexistente
        bad_resp = client.get("/api/v1/public/rma/NOEXIST-999")
        print(f"📡 GET /api/v1/public/rma/NOEXIST-999 -> {bad_resp.status_code}")
        assert bad_resp.status_code == 404
        print("✅ 404 correctamente para RMA inexistente")
    finally:
        db.close()


if __name__ == "__main__":
    test_public_tracking()
    print("\n🎉 Test de tracking público completado sin errores")