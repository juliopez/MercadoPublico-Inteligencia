#!/usr/bin/env bash
# Ejecución recuperable systemd: prepara conciliación, nunca aplica ni traslada Sheets.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export TZ=America/Santiago
mkdir -p logs
exec 7>"$ROOT/logs/.mer_escritura_compartida.lock"
flock -n 7 || { echo "MER ocupado: conciliación pendiente para siguiente intento";exit 0; }
[[ -x .venv/bin/python ]] || { echo "Falta entorno .venv" >&2;exit 1; }
# Capturar resultado de la puerta; sin cambios ni llamadas cuando no corresponde.
STATUS="$("$ROOT/.venv/bin/python" scripts/verificar_ventana_conciliacion.py)"
echo "$STATUS"
export STATUS
if ! "$ROOT/.venv/bin/python" - <<'PY'
import json,os,sys
r=json.loads(os.environ["STATUS"])
sys.exit(0 if r["estado"]=="PENDIENTE_CONCILIACION" else 1)
PY
then exit 0; fi
# Preparación oficial existente: descarga/importa/verifica, NO aplica ni traslada.
"$ROOT/.venv/bin/python" scripts/orquestar_cierre_mensual.py
echo "PREPARACION_HISTORICA_EJECUTADA: conciliación final aún requiere aprobación"
