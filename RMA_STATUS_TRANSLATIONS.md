# Traducciones de Estados de RMA

## Implementación

Se ha centralizado la traducción de los estados de RMA en un único lugar para mantener consistencia en toda la aplicación.

### Ubicación: `app/core/utils.py`

```python
# Diccionario de traducciones
RMA_STATUS_TRANSLATIONS: Dict[str, Dict[RMAStatus, str]] = {
    "es": {
        RMAStatus.RMA_SUBMITTED: "Solicitud Enviada",
        RMAStatus.AWAITING_GOODS: "Esperando Productos",
        RMAStatus.EVALUATING: "En Evaluación",
        RMAStatus.PROCESSING: "En Procesamiento",
        RMAStatus.PAYMENT: "Pago Pendiente",
        RMAStatus.IN_REPAIR: "En Reparación",
        RMAStatus.APPROVED: "Aprobado",
        RMAStatus.REJECTED: "Rechazado",
        RMAStatus.IN_SHIPPING: "En Envío",
        RMAStatus.COMPLETED: "Completado"
    },
    "en": {
        RMAStatus.RMA_SUBMITTED: "Request Submitted",
        RMAStatus.AWAITING_GOODS: "Awaiting Products",
        RMAStatus.EVALUATING: "Under Evaluation",
        RMAStatus.PROCESSING: "Processing",
        RMAStatus.PAYMENT: "Pending Payment",
        RMAStatus.IN_REPAIR: "Under Repair",
        RMAStatus.APPROVED: "Approved",
        RMAStatus.REJECTED: "Rejected",
        RMAStatus.IN_SHIPPING: "In Transit",
        RMAStatus.COMPLETED: "Completed"
    }
}
```

## Función Helper

```python
def get_rma_status_display(status: RMAStatus, language: str = "en") -> str:
    """
    Obtener el nombre traducido de un estado de RMA
    
    Args:
        status: Estado del RMA (enum)
        language: Código de idioma ('es' o 'en')
    
    Returns:
        Nombre del estado traducido
    """
```

## Uso en el Backend

### En CRUD (crud_rma.py)

```python
from app.core.utils import get_rma_status_display

# Obtener el nombre del estado en el idioma del usuario
status_display = get_rma_status_display(new_status, user.language.value)
```

### En Schemas (rma_public.py)

```python
from app.core.utils import get_rma_status_display

class RMAPublicResponse(BaseModel):
    @staticmethod
    def status_display_name(status: RMAStatus, language: str = "es") -> str:
        return get_rma_status_display(status, language)
```

## Uso en el Frontend

### Endpoint Público
El endpoint público `/api/v1/public/rma/{rma_number}` puede usar el método estático:

```python
# En Python
status_name_es = RMAPublicResponse.status_display_name(rma.status, "es")
status_name_en = RMAPublicResponse.status_display_name(rma.status, "en")
```

### Respuesta de API
El frontend puede:

1. **Opción 1**: Recibir el estado como enum y traducirlo localmente
```javascript
// Frontend mantiene su propio diccionario de traducciones
const statusTranslations = {
  es: {
    'rma_submitted': 'Solicitud Enviada',
    'awaiting_goods': 'Esperando Productos',
    // ... etc
  },
  en: {
    'rma_submitted': 'Request Submitted',
    'awaiting_goods': 'Awaiting Products',
    // ... etc
  }
}

const displayStatus = statusTranslations[userLanguage][rma.status]
```

2. **Opción 2**: Solicitar campo traducido del backend (requiere modificar respuesta)
```python
# Agregar campo computado en el schema
class RMAPublicResponse(BaseModel):
    # ... campos existentes
    status_display: Optional[str] = None
    
    @classmethod
    def from_orm_with_language(cls, rma, language: str = "es"):
        obj = cls.from_orm(rma)
        obj.status_display = get_rma_status_display(rma.status, language)
        return obj
```

## Estados Disponibles

| Enum Value | Español | English |
|-----------|---------|---------|
| `RMA_SUBMITTED` | Solicitud Enviada | Request Submitted |
| `AWAITING_GOODS` | Esperando Productos | Awaiting Products |
| `EVALUATING` | En Evaluación | Under Evaluation |
| `PROCESSING` | En Procesamiento | Processing |
| `PAYMENT` | Pago Pendiente | Pending Payment |
| `IN_REPAIR` | En Reparación | Under Repair |
| `APPROVED` | Aprobado | Approved |
| `REJECTED` | Rechazado | Rejected |
| `IN_SHIPPING` | En Envío | In Transit |
| `COMPLETED` | Completado | Completed |

## Archivos Modificados

- ✅ `app/core/utils.py` - Agregado diccionario y función helper
- ✅ `app/crud/crud_rma.py` - Reemplazado diccionario hardcoded por función centralizada
- ✅ `app/schemas/rma_public.py` - Actualizado método estático para usar función centralizada

## Ventajas

1. **Centralizado**: Una sola fuente de verdad para traducciones
2. **Reutilizable**: Se puede usar en cualquier parte del código
3. **Consistente**: Garantiza que todos los lugares usen las mismas traducciones
4. **Mantenible**: Agregar nuevos idiomas es fácil
5. **Type-safe**: Usa enums en lugar de strings

## Agregar Nuevos Idiomas

Para agregar un nuevo idioma (ejemplo: francés):

```python
RMA_STATUS_TRANSLATIONS: Dict[str, Dict[RMAStatus, str]] = {
    "es": { ... },
    "en": { ... },
    "fr": {
        RMAStatus.RMA_SUBMITTED: "Demande Soumise",
        RMAStatus.AWAITING_GOODS: "En Attente de Produits",
        RMAStatus.EVALUATING: "En Évaluation",
        RMAStatus.PROCESSING: "En Traitement",
        RMAStatus.PAYMENT: "Paiement en Attente",
        RMAStatus.IN_REPAIR: "En Réparation",
        RMAStatus.APPROVED: "Approuvé",
        RMAStatus.REJECTED: "Rejeté",
        RMAStatus.IN_SHIPPING: "En Transit",
        RMAStatus.COMPLETED: "Terminé"
    }
}
```

Y actualizar la validación:
```python
lang = language.lower() if language.lower() in ["es", "en", "fr"] else "en"
```

---

**Fecha**: Diciembre 12, 2025
**Estado**: ✅ Implementado
