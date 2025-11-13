# Script para iniciar servidor en MODO TESTING
# Recordatorios cada 3 segundos

Write-Host "⚡ INICIANDO SERVIDOR EN MODO TESTING" -ForegroundColor Yellow
Write-Host "════════════════════════════════════════" -ForegroundColor Yellow
Write-Host ""
Write-Host "Configuración:" -ForegroundColor Cyan
Write-Host "  ✓ Verificación cada: 3 SEGUNDOS" -ForegroundColor Green
Write-Host "  ✓ Recordatorios cada: 9 SEGUNDOS" -ForegroundColor Green
Write-Host "  ✓ Puerto: 8001" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  NO USAR EN PRODUCCIÓN" -ForegroundColor Red
Write-Host ""
Write-Host "════════════════════════════════════════" -ForegroundColor Yellow
Write-Host ""

# Activar entorno virtual si no está activo
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Activando entorno virtual..." -ForegroundColor Yellow
    & ".\venv\Scripts\Activate.ps1"
}

# Iniciar servidor
Write-Host "Iniciando servidor..." -ForegroundColor Green
Write-Host ""
uvicorn app.main_test:app --reload --port 8001
