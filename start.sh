#!/bin/bash
# Dashboard — Detalles Aleydy 🎀
# Arranca el servidor de administracion

cd "$(dirname "$0")"

echo "🎀 Iniciando Dashboard Detalles Aleydy..."
echo ""

# Verificar que el service account existe
if [ ! -f "keys/detalles-aleydy-firebase-sa.json" ]; then
    echo "❌ Service account no encontrado en keys/"
    exit 1
fi

# Instalar dependencias si no existen
pip3 install firebase-admin -q 2>/dev/null

echo "🚀 Arrancando servidor en http://localhost:5050"
echo "🔑 Token: aleyy-admin-2026"
echo ""

python3 admin.py
