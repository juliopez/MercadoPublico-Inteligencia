#!/usr/bin/env bash
# Preparación idempotente de pruebas sin escritura a Google Sheets.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
command -v python3 >/dev/null || { echo "Falta python3"; exit 1; }
python3 -c 'import sys; assert sys.version_info >= (3,9), "Se requiere Python >=3.9"'
mkdir -p .venv logs salida_operativa
if [[ ! -x .venv/bin/python ]]; then python3 -m venv .venv; fi
echo "Entorno preparado. No se instalaron paquetes ni se activó cron."
echo "Para primera prueba: bash scripts/ubuntu_probar_descargas.sh"
