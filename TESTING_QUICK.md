# ⚡ TESTING RÁPIDO - Recordatorios cada 3 segundos

## 🎯 Propósito

Esta configuración permite probar el sistema de recordatorios de pago de forma **extremadamente rápida** para verificar que todo funciona correctamente.

---

## ⚙️ Configuración de Testing

### Intervalos Configurados:

- **Verificación del scheduler**: Cada **3 SEGUNDOS**
- **Envío de recordatorios**: Cada **9 SEGUNDOS**

### Simulación de Días:

Los emails mostrarán "días pendientes" simulados basados en los ciclos:
- 9 segundos = 1 "día"
- 18 segundos = 2 "días"
- 27 segundos = 3 "días"

---

## 🚀 Cómo Ejecutar

### 1️⃣ Iniciar el Servidor en Modo Testing

```bash
# Opción 1: Usando el main_test.py
uvicorn app.main_test:app --reload --port 8001

# Opción 2: Si ya tienes el servidor normal corriendo en 8000
uvicorn app.main_test:app --reload --port 8002
```

### 2️⃣ Verificar que inició correctamente

Deberías ver en la consola:

```
🚀 Iniciando HighTech RMA System [TESTING MODE]...
⚡ Recordatorios configurados para SEGUNDOS (no días)
⚡ [TESTING MODE] Scheduler iniciado:
   └─> Verificación cada: 3 SEGUNDOS
   └─> Recordatorio cada: 9 SEGUNDOS
   ⚠️  NO USAR EN PRODUCCIÓN
```

### 3️⃣ Crear o Cambiar un RMA a estado PAYMENT

Usa la API para cambiar un RMA existente a estado `PAYMENT`:

```bash
# Endpoint: PUT /api/v1/rmas/{rma_id}/status
# Body:
{
  "new_status": "payment"
}
```

### 4️⃣ Observar los Logs

En la consola verás algo como:

```
🔍 [TEST] Verificando recordatorios (cada 3s, envío cada 9s)...
   RMA HTR-2024-USA-0001: 3s desde última verificación
      └─> Esperando 6s más para próximo recordatorio
   
# 6 segundos después...

🔍 [TEST] Verificando recordatorios (cada 3s, envío cada 9s)...
   RMA HTR-2024-USA-0001: 9s desde última verificación
✅ [TEST] Recordatorio enviado: RMA HTR-2024-USA-0001 (9s = 1 'días' simulados)
📧 Email enviado a usuario@email.com: ⏰ Recordatorio: Pago Pendiente

# 9 segundos después...

🔍 [TEST] Verificando recordatorios (cada 3s, envío cada 9s)...
   RMA HTR-2024-USA-0001: 18s desde última verificación
✅ [TEST] Recordatorio enviado: RMA HTR-2024-USA-0001 (18s = 2 'días' simulados)
```

---

## 📧 Emails que Recibirás

### Primera vez (9 segundos / 1 "día"):
```
Asunto: ⏰ Recordatorio: Pago Pendiente - RMA HTR-XXX
Color: 🟡 Amarillo
Mensaje: "Tu RMA está en espera de pago..."
Días pendientes: 1
```

### Segunda vez (18 segundos / 2 "días"):
```
Asunto: ⏰ Recordatorio: Pago Pendiente - RMA HTR-XXX
Color: 🟠 Naranja
Mensaje: "Te recordamos que el pago sigue pendiente..."
Días pendientes: 2
```

### Tercera vez (27 segundos / 3 "días"):
```
Asunto: ⏰ Recordatorio: Pago Pendiente - RMA HTR-XXX
Color: 🔴 Rojo
Mensaje: "Este es un recordatorio importante..."
Días pendientes: 3
```

---

## 🎬 Cronología de Prueba Completa

```
Tiempo 0s   │ Iniciar servidor en modo testing
            │ RMA ya existe en estado PAYMENT
            │
Tiempo 3s   │ Primera verificación
            │ ⏳ Solo 3s transcurridos, esperando 6s más
            │
Tiempo 6s   │ Segunda verificación
            │ ⏳ Solo 6s transcurridos, esperando 3s más
            │
Tiempo 9s   │ Tercera verificación
            │ ✅ 9s completados → ENVÍA EMAIL #1 (🟡 Amarillo)
            │
Tiempo 12s  │ Verificación
            │ ⏳ Solo 3s desde último email, esperando 6s más
            │
Tiempo 15s  │ Verificación
            │ ⏳ Solo 6s desde último email, esperando 3s más
            │
Tiempo 18s  │ Verificación
            │ ✅ 9s desde último email → ENVÍA EMAIL #2 (🟠 Naranja)
            │
Tiempo 27s  │ Verificación
            │ ✅ 9s desde último email → ENVÍA EMAIL #3 (🔴 Rojo)
            │
Tiempo 36s  │ Verificación
            │ ✅ 9s desde último email → ENVÍA EMAIL #4 (🔴 Rojo)
```

---

## 🛑 Detener Recordatorios

### Opción 1: Cambiar Estado del RMA

Cambia el RMA a cualquier otro estado (por ejemplo `in_shipping`):

```bash
# Endpoint: PUT /api/v1/rmas/{rma_id}/status
# Body:
{
  "new_status": "in_shipping",
  "shipping_company": "FedEx",
  "tracking_id": "TEST123"
}
```

Verás en logs:
```
🔕 Recordatorios de pago detenidos para RMA HTR-2024-USA-0001
```

### Opción 2: Detener el Servidor

Simplemente presiona `Ctrl+C` en la terminal.

---

## ⚠️ ADVERTENCIAS IMPORTANTES

### 🚫 NO USAR EN PRODUCCIÓN

Este modo es **SOLO PARA TESTING**. En producción:
- Los recordatorios deben enviarse cada **días** (no segundos)
- Usa el `main.py` normal (no `main_test.py`)
- Configuración recomendada: 3 días de intervalo, verificación cada 24 horas

### 📧 Cuidado con el Email

Con esta configuración **enviarás muchos emails muy rápido**:
- 1 email cada 9 segundos
- ~400 emails por hora si el RMA permanece en PAYMENT

**Recomendaciones**:
1. Usa un email de prueba (no uno real de cliente)
2. Prueba solo por 1-2 minutos
3. Cambia el estado del RMA después de verificar
4. Verifica que `EMAIL_ENABLED=true` en `.env`

---

## 🧪 Checklist de Prueba

- [ ] Servidor iniciado con `uvicorn app.main_test:app --reload --port 8001`
- [ ] Logs muestran "TESTING MODE" y configuración de segundos
- [ ] RMA creado y cambiado a estado `PAYMENT`
- [ ] Primer recordatorio recibido después de ~9 segundos
- [ ] Segundo recordatorio recibido después de ~18 segundos
- [ ] Colores de emails cambian según tiempo (amarillo → naranja → rojo)
- [ ] Al cambiar RMA a `in_shipping`, recordatorios se detienen
- [ ] Email recibido con confirmación de nuevo estado

---

## 🔄 Volver a Modo Normal

Cuando termines las pruebas:

1. **Detener el servidor de testing** (`Ctrl+C`)

2. **Iniciar el servidor normal**:
```bash
uvicorn app.main:app --reload
```

3. **Verificar configuración normal**:
```bash
python app/scripts/check_config_simple.py
```

Deberías ver:
```
🕐 Scheduler iniciado: recordatorios cada 24h, intervalo de envío 3 días
```

---

## 📊 Comparativa

| Aspecto | Modo Normal | Modo Testing |
|---------|-------------|--------------|
| **Archivo** | `main.py` | `main_test.py` |
| **Verificación** | Cada 24 horas | Cada 3 segundos |
| **Recordatorios** | Cada 3 días | Cada 9 segundos |
| **Uso** | Producción | Testing solamente |
| **Puerto sugerido** | 8000 | 8001 o 8002 |

---

## 💡 Tips

1. **Logs en tiempo real**: Observa la consola para ver cada verificación
2. **Email test**: Usa un servicio como Mailtrap o un email de prueba
3. **Cambio rápido**: Mantén Postman/Insomnia abierto para cambiar estados rápidamente
4. **Múltiples RMAs**: Puedes probar con varios RMAs en estado PAYMENT simultáneamente
5. **Base de datos**: Usa la BD de desarrollo, no producción

---

¿Preguntas? Revisa la documentación completa en `docs/PAYMENT_REMINDERS_CONFIG.md`
