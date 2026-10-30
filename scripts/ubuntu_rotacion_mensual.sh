#!/usr/bin/env bash
# Rotación mensual protegida; no altera el cron Ubuntu de las 16.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export TZ=America/Santiago
export GOOGLE_APPLICATION_CREDENTIALS="${GOOGLE_APPLICATION_CREDENTIALS:-$HOME/.config/mercadopublico/servicio-google.json}"
mkdir -p logs
exec 8>"$ROOT/logs/.mer_escritura_compartida.lock"
flock -n 8 || { echo "MER ocupado; rotación aplazada";exit 0; }
test -x "$ROOT/.venv/bin/python" || { echo "Falta .venv" >&2; exit 1; }
"$ROOT/.venv/bin/python" scripts/rotar_mes_operativo.py --aplicar
