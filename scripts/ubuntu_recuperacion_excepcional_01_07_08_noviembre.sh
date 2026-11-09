#!/usr/bin/env bash
# Recuperacion excepcional de los listados del 01, 07 y 08/11/2026.
# Recupera detalles, carga MER operativo y publica V2; no instala cron.
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
[[ "$MES" == "2026-11" ]] || { echo "BLOQUEO: ejecutar solo durante el mes operativo 2026-11"; exit 3; }
for DIA in 01 07 08; do
  FECHA="2026-11-$DIA"
  DIR="$HOME/mercadopublico-recuperacion-licitaciones/excepcional-$FECHA"
  echo "INICIO_DIA $FECHA $(date --iso-8601=seconds)"
  # Directorio separado para no alterar el checkpoint del cron diario.
  python3 scripts/recuperar_licitaciones_api.py \
    --desde "$FECHA" --hasta "$FECHA" --mes "$MES" \
    --limite 0 --pausa 10 --refrescar-ultimo --solo-dia --directorio "$DIR"
  "$ROOT/.venv/bin/python" - "$DIR/informe.json" <<'PY'
import json,sys
r=json.load(open(sys.argv[1],encoding="utf-8"))
print("VALIDACION_DIA",r["codigos_unicos_listados"],r["detalles_guardados"],r["pendientes"])
if r["pendientes"]!=0:
    raise SystemExit("BLOQUEO: detalles pendientes, no se considera completo el dia")
PY
  (
    exec 8>"$ROOT/logs/.mer_escritura_compartida.lock"
    flock -w 3600 8 || { echo "BLOQUEO: MER ocupado"; exit 5; }
    "$ROOT/.venv/bin/python" scripts/cargar_licitaciones_api_mer.py \
      --csv "$DIR/todos_los_periodos.csv" --aplicar
  )
  echo "MER_DIA_VERIFICADO $FECHA $(date --iso-8601=seconds)"
done
bash scripts/ubuntu_publicar_v2_post_etl.sh --aplicar
echo "RECUPERACION_EXCEPCIONAL_COMPLETA $(date --iso-8601=seconds)"
