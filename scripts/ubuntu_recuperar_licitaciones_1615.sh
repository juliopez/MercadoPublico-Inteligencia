#!/usr/bin/env bash
# Recoleccion API licitaciones 16:15 Santiago. Solo checkpoint local; no MER ni publicacion.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export TZ=America/Santiago
cd "$ROOT"
mkdir -p logs
exec 9>"$ROOT/logs/.recuperacion_licitaciones_api.lock"
flock -n 9 || { echo "RECUPERACION_YA_EN_CURSO"; exit 0; }
ENV_FILE="$HOME/.config/mercadopublico/api.env"
[[ -r "$ENV_FILE" ]] || { echo "BLOQUEO: falta archivo de credenciales local"; exit 2; }
set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a
: "${CHILECOMPRA_TICKET:?BLOQUEO: ticket no configurado}"
MES="$(date +%Y-%m)"
HOY="$(date +%F)"
DESDE="${MER_LIC_API_DESDE:-$MES-01}"
LIMITE="${MER_LIC_API_LIMITE:-400}"
echo "INICIO_RECUPERACION fecha=$HOY mes=$MES limite=$LIMITE"
exec python3 scripts/recuperar_licitaciones_api.py \
  --desde "$DESDE" --hasta "$HOY" --mes "$MES" --limite "$LIMITE" --pausa 10
