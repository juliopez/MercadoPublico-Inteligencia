#!/usr/bin/env bash
# Instalación supervisada del cron API nocturno en EL MISMO Ubuntu que ejecuta el ETL.
# No se ejecuta automáticamente al incorporar el archivo al repositorio.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PY="$ROOT/.venv/bin/python"
test -x "$PY" || { echo "ERROR: falta venv del cron operativo"; exit 2; }
GOOGLE_APPLICATION_CREDENTIALS="${GOOGLE_APPLICATION_CREDENTIALS:-$HOME/.config/mercadopublico/servicio-google.json}"
test -r "$GOOGLE_APPLICATION_CREDENTIALS" || { echo "ERROR: no se encuentra la credencial Google del ETL"; exit 3; }
TICKET_FILE="${CHILECOMPRA_TICKET_FILE:-$HOME/.config/mercadopublico/chilecompra_ticket}"
if [[ -z "${CHILECOMPRA_TICKET:-}" ]]; then
  test -r "$TICKET_FILE" || { echo "ERROR: configurar ticket API privado para usuario Ubuntu"; exit 4; }
  export CHILECOMPRA_TICKET
  CHILECOMPRA_TICKET="$(tr -d '\r\n' < "$TICKET_FILE")"
fi
test -n "$CHILECOMPRA_TICKET" || { echo "ERROR: ticket vacío"; exit 5; }
export GOOGLE_APPLICATION_CREDENTIALS
export MER_API_MAX_DETAIL=2
mkdir -p "$ROOT/logs"
exec 8>"$ROOT/logs/.api_2230.lock"
flock -n 8 || { echo "Otro lote API sigue ejecutándose"; exit 0; }
# Pide el módulo de Google existente, no instala paquetes ni modifica venv/cron.
"$PY" -c 'import gspread,google.auth'
"$PY" scripts/sincronizar_tres_tablas_api_2230.py
