# Implementación de Emails Multiidioma

## Resumen
Se ha implementado soporte completo para emails en **español** e **inglés** en todo el sistema de notificaciones por correo electrónico. Los emails se envían automáticamente en el idioma preferido del usuario.

## Cambios Principales

### 1. Servicio de Email (`app/services/email_service.py`)

#### Traducciones Agregadas
Se agregó un diccionario completo `EMAIL_TRANSLATIONS` con traducciones en español e inglés para todos los tipos de email:

- **welcome**: Email de bienvenida al registrarse
- **admin_welcome**: Email de bienvenida para usuarios creados por admin/superadmin
- **password_reset**: Email de recuperación de contraseña
- **rma_created**: Email cuando se crea un RMA
- **rma_approved**: Email cuando se aprueba un RMA
- **rma_rejected**: Email cuando se rechaza un RMA
- **rma_quote_uploaded**: Email cuando se sube cotización/factura
- **rma_shipping**: Email cuando el RMA está en envío
- **rma_completed**: Email cuando se completa un RMA
- **rma_status_change**: Email genérico de cambio de estado
- **payment_reminder**: Email de recordatorio de pago pendiente

#### Método Helper Agregado
```python
@staticmethod
def _get_translation(language: str, section: str) -> Dict[str, str]:
    """
    Obtener traducciones para un idioma y sección específica
    
    Args:
        language: Código de idioma ('es' o 'en')
        section: Sección de traducción
    
    Returns:
        Diccionario con traducciones
    """
```

#### Métodos Actualizados
Todos los métodos de envío de email ahora aceptan el parámetro `language`:

- `send_welcome_email(user_email, user_name, language="en")`
- `send_admin_welcome_email(user_email, user_name, user_role, temp_password, language="en")`
- `send_password_reset_email(user_email, user_name, reset_token, reset_url, language="en")`
- `send_rma_created_email(..., language="en")`
- `send_rma_approved_email(..., language="en")`
- `send_rma_rejected_email(..., language="en")`
- `send_rma_quote_uploaded_email(..., language="en")`
- `send_rma_shipping_email(..., language="en")`
- `send_rma_completed_email(..., language="en")`
- `send_rma_status_change_email(..., language="en")`
- `send_payment_reminder_email(..., language="en")`

### 2. Archivos Actualizados con Idioma del Usuario

#### `app/api/v1/endpoints/auth.py`
- Agregado `language=user.language.value` al enviar email de bienvenida en registro

#### `app/api/v1/endpoints/users.py`
- Agregado `language=user.language.value` al enviar email de bienvenida cuando un admin crea un usuario

#### `app/api/v1/endpoints/password_reset.py`
- Agregado `language=user.language.value` al enviar email de recuperación de contraseña

#### `app/api/v1/endpoints/attachments.py`
- Agregado `language=creator.language.value` al enviar emails de cotización/factura cargada
- Actualizado tanto para carga inicial como para reemplazo de archivos

#### `app/crud/crud_rma.py`
- Agregado `language=user.language.value` en todos los emails de cambio de estado:
  - RMA creado
  - RMA aprobado
  - RMA rechazado
  - RMA en envío
  - RMA completado
  - Cambios de estado genéricos

#### `app/services/scheduler_service.py`
- Agregado `language=user.language.value` al enviar recordatorios automáticos de pago

## Funcionamiento

### Detección Automática del Idioma
Cuando se envía un email, el sistema:
1. Obtiene el idioma preferido del usuario desde su perfil (`user.language`)
2. Pasa el idioma al método de email correspondiente
3. El método `_get_translation()` recupera las traducciones apropiadas
4. El HTML del email se genera usando las cadenas traducidas

### Idiomas Soportados
- **Español** (`es`): Idioma por defecto en la base de datos existente
- **Inglés** (`en`): Idioma alternativo

### Fallback
Si se proporciona un idioma no soportado, el sistema usa inglés por defecto:
```python
lang = language.lower() if language.lower() in ["es", "en"] else "en"
```

## Ejemplo de Uso

```python
# El idioma se toma automáticamente del usuario
email_service.send_welcome_email(
    user_email=user.email,
    user_name=user.full_name,
    language=user.language.value  # 'es' o 'en'
)
```

## Contenido Traducido

Cada tipo de email incluye traducciones completas de:
- Asuntos de correo
- Títulos y encabezados
- Saludos y despedidas
- Mensajes informativos
- Instrucciones paso a paso
- Notas y advertencias
- Firmas
- Textos legales (footer)

## Compatibilidad

✅ **Compatibilidad Total**: Todos los emails existentes en el sistema ahora soportan multiidioma sin cambios en la lógica de negocio, solo se agregó el parámetro `language` que toma el valor del usuario automáticamente.

## Próximos Pasos (Opcional)

Si se desea expandir:
1. Agregar más idiomas (francés, portugués, etc.)
2. Externalizar traducciones a archivos JSON
3. Permitir que usuarios cambien su idioma desde el frontend
4. Agregar traducciones para estados de RMA personalizados

## Verificación

Para verificar que funciona correctamente:
1. Crear un usuario con idioma español
2. Crear un usuario con idioma inglés
3. Realizar acciones que disparen emails (registro, cambio de estado de RMA, etc.)
4. Verificar que los emails lleguen en el idioma correcto

---

**Fecha de Implementación**: Diciembre 12, 2025
**Estado**: ✅ Completado y listo para producción
