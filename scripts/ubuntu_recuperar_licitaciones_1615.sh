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
LIMITE=0 # Sin cuota diaria: todos los detalles pendientes
echo "INICIO_LICITACIONES_API $(date --iso-8601=seconds) mes=$MES limite=$LIMITE"
python3 scripts/recuperar_licitaciones_api.py --desde "$DESDE" --hasta "$HOY" --mes "$MES" --limite "$LIMITE" --pausa 10 --refrescar-ultimo
CSV="$HOME/mercadopublico-recuperacion-licitaciones/masivo/procesos_mes.csv"
[[ -s "$CSV" ]] || { echo "BLOQUEO: CSV no generado"; exit 3; }
# El candado compartido protege las escrituras MER; no bloquear durante consultas API.
exec 8>"$ROOT/logs/.mer_escritura_compartida.lock"
flock -w 3600 8 || { echo "BLOQUEO: MER ocupado"; exit 5; }
"$ROOT/.venv/bin/python" scripts/cargar_licitaciones_api_mer.py --csv "$CSV" --aplicar
flock -u 8
# La publicación protegida exige una carga diaria previa del ETL de las 16:00.
# Si no existe esa evidencia, el comando falla sin publicar datos no certificados.
bash scripts/ubuntu_publicar_v2_post_etl.sh --aplicar
echo "LICITACIONES_API_PUBLICADAS $(date --iso-8601=seconds)"
