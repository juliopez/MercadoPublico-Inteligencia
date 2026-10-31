#!/usr/bin/env bash
# Ejecución recuperable systemd: prepara, concilia, publica y verifica el histórico.
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
# Cierre automático; ante errores no declara éxito y systemd reintentará.
export GOOGLE_APPLICATION_CREDENTIALS="${GOOGLE_APPLICATION_CREDENTIALS:-$HOME/.config/mercadopublico/servicio-google.json}"
"$ROOT/.venv/bin/python" scripts/cierre_mensual_automatico.py
echo "CIERRE_AUTOMATICO_EJECUTADO: verificar estado_cierre.json"
