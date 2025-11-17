# 🔧 HighTech RMA System - Backend

Sistema de gestión de RMA (Return Merchandise Authorization) para HighTech Supplies.

## 🚀 Instalación

```bash
# Clonar repositorio
git clone <tu-repo>
cd hightech-rma-backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

## 🌐 Endpoint Público de Tracking de RMA

Ahora puedes consultar el estado y evolución de un RMA sin autenticación usando su `rma_number`.

### URL

```
GET /api/v1/public/rma/{rma_number}
```

### Ejemplo de respuesta

```json
{
	"rma_number": "RMA-TL-2025-00002",
	"status": "approved",
	"company_name": "Empresa Demo",
	"company_address": "Calle Falsa 123",
	"postal_code": "0001",
	"country_id": 12,
	"created_at": "2025-11-17T05:03:54.811456",
	"updated_at": "2025-11-17T05:03:55.639997",
	"shipping_company": null,
	"tracking_id": null,
	"items": [
		{
			"id": 38,
			"serial_number": "SN-DEMO-3795f50e",
			"service_type": "repair",
			"issue_description": "No enciende",
			"brand_id": 6,
			"brand_name": "BrandX",
			"product_id": 7,
			"product_name": "ProductoX",
			"model_id": 11,
			"model_name": "ModeloX"
		}
	],
	"history": [
		{
			"previous_status": null,
			"new_status": "rma_submitted",
			"changed_at": "2025-11-17T05:03:54.816459",
			"comment": "RMA creado"
		},
		{
			"previous_status": "rma_submitted",
			"new_status": "approved",
			"changed_at": "2025-11-17T05:03:55.637984",
			"comment": "Aprobado para seguimiento"
		}
	]
}
```

### Notas

- No devuelve PDFs ni adjuntos (documentos privados).
- Incluye historial completo de cambios de estado.
- Los nombres de marca, producto y modelo se devuelven para cada item.
- Devuelve 404 si el `rma_number` no existe.

### Prueba rápida

Ejecuta el script de prueba (crea datos mínimos y valida el endpoint):

```bash
python test_public_rma_tracking.py
```
