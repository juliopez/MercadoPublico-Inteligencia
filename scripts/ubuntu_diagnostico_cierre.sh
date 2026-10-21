#!/usr/bin/env bash
# Diagnóstico supervisado de cierre MER v2, serializado con el ETL diario.
# SIN escrituras en Sheets, SIN traslado Drive ni actualización del catálogo.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
if [[ ! -x "$ROOT/.venv/bin/python" ]]; then
 echo "ERROR: falta entorno .venv" >&2; exit 2
fi
mkdir -p "$ROOT/logs"
exec 8>"$ROOT/logs/.mer_escritura_compartida.lock"
flock -n 8 || { echo "Bloqueo MER ocupado por el ETL o por otro cierre; no se inicia" >&2; exit 5; }
export TZ=America/Santiago
export GOOGLE_APPLICATION_CREDENTIALS="${GOOGLE_APPLICATION_CREDENTIALS:-$HOME/.config/mercadopublico/servicio-google.json}"
if [[ ! -r "$GOOGLE_APPLICATION_CREDENTIALS" ]]; then
 echo "ERROR: falta credencial Google local legible" >&2; exit 3
fi
STAMP="$(date +%Y%m%d_%H%M%S)"
LOG="$ROOT/logs/diagnostico_cierre_$STAMP.log"
printf 'INICIO %s DIAGNOSTICO SIN ESCRITURAS\n' "$(date --iso-8601=seconds)" | tee "$LOG"
set +e
"$ROOT/.venv/bin/python" scripts/diagnosticar_cierre_integrado.py "$@" 2>&1 | tee -a "$LOG"
STATUS=${PIPESTATUS[0]}
set -e
printf 'FIN %s CODIGO=%s\n' "$(date --iso-8601=seconds)" "$STATUS" | tee -a "$LOG"
exit "$STATUS"
