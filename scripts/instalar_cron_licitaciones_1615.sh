#!/usr/bin/env bash
# Instalador idempotente del cron de licitaciones API a las 16:15.
# Ejecutar desde el repositorio despues de validar la primera carga/publicacion.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
[[ -f scripts/recuperar_licitaciones_api.py && -f scripts/cargar_licitaciones_api_mer.py ]] || { echo "Faltan scripts"; exit 2; }
[[ -x .venv/bin/python ]] || { echo "Falta entorno virtual"; exit 2; }
[[ -r "$HOME/.config/mercadopublico/api.env" ]] || { echo "Falta api.env"; exit 2; }
[[ -r "$HOME/.config/mercadopublico/servicio-google.json" ]] || { echo "Falta credencial Google"; exit 2; }
# Cron interpreta horas en el huso del sistema; no asumir soporte CRON_TZ.
[[ "$(date +%z)" == "$(TZ=America/Santiago date +%z)" ]] || {
  echo "BLOQUEO: huso horario local distinto a Santiago. No se instala cron"; exit 3;
}
python3 -m py_compile scripts/recuperar_licitaciones_api.py scripts/cargar_licitaciones_api_mer.py
bash -n scripts/ubuntu_dispatch_licitaciones_1615.sh
mkdir -p logs
TAG="# MER_LICITACIONES_API_1615"
ENTRY="15 16 * * 1-5 /bin/bash \"$ROOT/scripts/ubuntu_dispatch_licitaciones_1615.sh\" >> \"$ROOT/logs/licitaciones_api_1615_dispatch.log\" 2>&1 $TAG"
CURRENT="$(crontab -l 2>/dev/null || true)"
CURRENT="$(printf '%s\n' "$CURRENT" | grep -v -F "$TAG" || true)"
printf '%s\n%s\n' "$CURRENT" "$ENTRY" | crontab -
echo "CRON_INSTALADO: lunes a viernes 16:15 hora local (America/Santiago)"
crontab -l | grep -F "$TAG"
