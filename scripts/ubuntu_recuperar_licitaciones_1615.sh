#!/usr/bin/env bash
# 16:15 Chile: recuperar licitaciones, actualizar MER y publicar Observatorio V2.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export TZ=America/Santiago
export GOOGLE_APPLICATION_CREDENTIALS="${GOOGLE_APPLICATION_CREDENTIALS:-$HOME/.config/mercadopublico/servicio-google.json}"
mkdir -p logs salida_operativa
exec 9>"$ROOT/logs/.recuperacion_licitaciones_api.lock"
flock -n 9 || { echo "RECUPERACION_YA_EN_CURSO"; exit 0; }
ENV_FILE="$HOME/.config/mercadopublico/api.env"
[[ -r "$ENV_FILE" ]] || { echo "BLOQUEO: credenciales API ausentes"; exit 2; }
set -a
source "$ENV_FILE"
set +a
: "${CHILECOMPRA_TICKET:?BLOQUEO: ticket ausente}"
MES="$(date +%Y-%m)"
HOY="$(date +%F)"
DESDE="${MER_LIC_API_DESDE:-$MES-01}"
# Lotes operativos para publicar progresivamente, sin cuota diaria total.
LOTE=200
CSV="$HOME/mercadopublico-recuperacion-licitaciones/masivo/procesos_mes.csv"
INFORME="$HOME/mercadopublico-recuperacion-licitaciones/masivo/informe.json"
ANTERIOR=-1
while true; do
  echo "LOTE_LICITACIONES_API $(date --iso-8601=seconds) mes=$MES"
  python3 scripts/recuperar_licitaciones_api.py --desde "$DESDE" --hasta "$HOY" --mes "$MES" --limite "$LOTE" --pausa 10 --refrescar-ultimo
  [[ -s "$CSV" && -s "$INFORME" ]] || { echo "BLOQUEO: salida de recuperacion ausente"; exit 3; }
  # El candado compartido protege las escrituras MER, sin bloquear las consultas.
  (
    exec 8>"$ROOT/logs/.mer_escritura_compartida.lock"
    flock -w 3600 8 || { echo "BLOQUEO: MER ocupado"; exit 5; }
    "$ROOT/.venv/bin/python" scripts/cargar_licitaciones_api_mer.py --csv "$CSV" --aplicar
  )
  # Publicar despues de cada lote, no solo al agotar una cola extensa.
  bash scripts/ubuntu_publicar_v2_post_etl.sh --aplicar
  PENDIENTES="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["pendientes"])' "$INFORME")"
  echo "PENDIENTES_API=$PENDIENTES"
  [[ "$PENDIENTES" -eq 0 ]] && break
  if [[ "$ANTERIOR" -eq "$PENDIENTES" ]]; then
    echo "BLOQUEO: sin avance en cola API, revisar errores; no repetir indefinidamente" >&2
    exit 7
  fi
  ANTERIOR="$PENDIENTES"
done
echo "LICITACIONES_API_PUBLICADAS $(date --iso-8601=seconds)"
