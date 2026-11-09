#!/usr/bin/env bash
# Instala cron idempotente, lunes a viernes 09:00 hora de Santiago.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
[[ -x .venv/bin/python ]] || { echo "FALTA_VENV";exit 2; }
[[ -r "$HOME/.config/mercadopublico/servicio-google.json" ]] || { echo "FALTA_CREDENCIAL";exit 2; }
[[ "$(date +%z)" == "$(TZ=America/Santiago date +%z)" ]] || { echo "BLOQUEO_ZONA_HORARIA";exit 3; }
.venv/bin/python -m py_compile scripts/conciliar_mer_cronologico.py scripts/exportar_mer_operativo_v2.py
bash -n scripts/ubuntu_conciliar_mer_0900.sh
mkdir -p logs
TAG="# MER_CONCILIACION_0900"
ENTRY="0 9 * * 1-5 /bin/bash \"$ROOT/scripts/ubuntu_conciliar_mer_0900.sh\" >> \"$ROOT/logs/conciliacion_mer_0900.log\" 2>&1 $TAG"
CURRENT="$(crontab -l 2>/dev/null || true)"
if printf '%s\n' "$CURRENT" | grep -Fq "$TAG";then
 echo "CRON_EXISTENTE";crontab -l | grep -F "$TAG";exit 0
fi
printf '%s\n%s\n' "$CURRENT" "$ENTRY" | crontab -
echo "CRON_INSTALADO: lunes a viernes 09:00 America/Santiago"
crontab -l | grep -F "$TAG"
