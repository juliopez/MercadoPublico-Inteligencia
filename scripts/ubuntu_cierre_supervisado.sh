#!/usr/bin/env bash
# Entrada única para cierre manual supervisado, NO programa cron.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
mkdir -p logs
exec 8>"$ROOT/logs/.mer_escritura_compartida.lock"
flock -n 8 || { echo "CIERRE BLOQUEADO: ETL/cierre simultáneo";exit 5; }
export TZ=America/Santiago
export GOOGLE_APPLICATION_CREDENTIALS="${GOOGLE_APPLICATION_CREDENTIALS:-$HOME/.config/mercadopublico/servicio-google.json}"
[[ -x .venv/bin/python ]] || { echo "Falta .venv/bin/python";exit 2; }
MODE="${1:-}";shift || true
STAMP="$(date +%Y%m%d_%H%M%S)"
LOG="$ROOT/logs/cierre_supervisado_$STAMP.log"
case "$MODE" in
 verificar-acceso) COMMAND=(.venv/bin/python scripts/ejecutar_cierre_supervisado.py --verificar-acceso --periodo "${1:-2026-10}");;
 diagnosticar) COMMAND=(.venv/bin/python scripts/diagnosticar_cierre_integrado.py "$@");;
 cargar) COMMAND=(.venv/bin/python scripts/ejecutar_cierre_supervisado.py --cargar --confirmar-carga "$@");;
 trasladar) COMMAND=(.venv/bin/python scripts/ejecutar_cierre_supervisado.py --trasladar --confirmar-traslado "$@");;
 *) echo "Uso: bash scripts/ubuntu_cierre_supervisado.sh verificar-acceso|diagnosticar|cargar|trasladar --periodo AAAA-MM";exit 2;;
esac
echo "INICIO $MODE $(date --iso-8601=seconds)" | tee "$LOG"
set +e
"${COMMAND[@]}" 2>&1 | tee -a "$LOG"
STATUS=${PIPESTATUS[0]}
set -e
echo "FIN $MODE CODIGO=$STATUS $(date --iso-8601=seconds)" | tee -a "$LOG"
exit "$STATUS"
