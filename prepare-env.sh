#!/bin/bash
# Script para copiar .env.railway a .env si no existe
# Usado durante el build en Railway

if [ ! -f .env ]; then
    echo "📋 Copiando .env.railway a .env para el build..."
    cp .env.railway .env
else
    echo "✅ .env ya existe"
fi
