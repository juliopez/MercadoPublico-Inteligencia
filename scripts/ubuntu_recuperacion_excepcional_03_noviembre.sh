#!/usr/bin/env bash
# Recuperacion excepcional del listado API del 03/11/2026.
# Carga en MER operativo y publica V2; no instala ni modifica cron.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export TZ=America/Santiago
export GOOGLE_APPLICATION_CREDENTIALS="${GOOGLE_APPLICATION_CREDENTIALS:-$HOME/.config/mercadopublico/servicio-google.json}"
mkdir -p logs salida_operativa
exec 9>"$ROOT/logs/.recuperacion_licitaciones_api.lock"
flock -n 9 || { echo "BLOQUEO: otra recuperacion API activa"; exit 4; }
ENV_FILE="$HOME/.config/mercadopublico/api.env"
[[ -r "$ENV_FILE" ]] || { echo "BLOQUEO: credenciales API ausentes"; exit 2; }
set -a
source "$ENV_FILE"
set +a
: "${CHILECOMPRA_TICKET:?BLOQUEO: ticket ausente}"
MES="$(date +%Y-%m)"
[[ "$MES" == "2026-11" ]] || { echo "BLOQUEO: requiere MER operativo 2026-11"; exit 3; }
FECHA=2026-11-03
DIR="$HOME/mercadopublico-recuperacion-licitaciones/excepcional-$FECHA"
LOTE=200
ANTERIOR=-1
while true; do
  echo "RECUPERACION_DIA $FECHA $(date --iso-8601=seconds)"
  python3 scripts/recuperar_licitaciones_api.py \
    --desde "$FECHA" --hasta "$FECHA" --mes "$MES" \
    --limite "$LOTE" --pausa 10 --refrescar-ultimo --solo-dia --directorio "$DIR"
  PENDIENTES="$("$ROOT/.venv/bin/python" - "$DIR/informe.json" <<'PY'
import json,sys
r=json.load(open(sys.argv[1],encoding="utf-8"))
print(r["pendientes"])
PY
)"
  (
    exec 8>"$ROOT/logs/.mer_escritura_compartida.lock"
    flock -w 3600 8 || { echo "BLOQUEO: MER ocupado"; exit 5; }
    "$ROOT/.venv/bin/python" scripts/cargar_licitaciones_api_mer.py \
      --csv "$DIR/todos_los_periodos.csv" --aplicar
  )
  echo "CARGA_LOTE_VERIFICADA $FECHA pendientes=$PENDIENTES"
  bash scripts/ubuntu_publicar_v2_post_etl.sh --aplicar
  [[ "$PENDIENTES" -eq 0 ]] && break
  if [[ "$ANTERIOR" -eq "$PENDIENTES" ]]; then
    echo "BLOQUEO: no hay avance en la recuperacion; revisar errores" >&2
    exit 7
  fi
  ANTERIOR="$PENDIENTES"
done
echo "RECUPERACION_03_NOVIEMBRE_COMPLETA $(date --iso-8601=seconds)"
