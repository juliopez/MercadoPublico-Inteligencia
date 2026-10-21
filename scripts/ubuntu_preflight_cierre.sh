#!/usr/bin/env bash
# Preflight supervisado del cierre, protegido por el mismo flock que el ETL diario.
# No modifica Sheets ni mueve archivos, y NO ejecuta el cargador real.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
mkdir -p logs
PERIODO="${1:?Uso: bash scripts/ubuntu_preflight_cierre.sh AAAA-MM}"
[[ "$PERIODO" =~ ^[0-9]{4}-[0-9]{2}$ ]] || { echo "Período inválido" >&2; exit 2; }
[[ -x "$ROOT/.venv/bin/python" ]] || { echo "Falta .venv" >&2; exit 3; }
export GOOGLE_APPLICATION_CREDENTIALS="${GOOGLE_APPLICATION_CREDENTIALS:-$HOME/.config/mercadopublico/servicio-google.json}"
[[ -r "$GOOGLE_APPLICATION_CREDENTIALS" ]] || { echo "Faltan credenciales" >&2; exit 4; }
BASE="$HOME/.local/share/mercadopublico/cierres/$PERIODO"
# Bloqueo mantenido por todo el shell, incluidas lecturas y futuras fases.
exec 8>"$ROOT/logs/.mer_escritura_compartida.lock"
flock -n 8 || { echo "ETL diario o cierre ya ejecutándose; no se superpone" >&2; exit 5; }
"$ROOT/.venv/bin/python" scripts/revalidar_operativo_cierre.py --conciliacion "$BASE/conciliacion.json"
"$ROOT/.venv/bin/python" scripts/simular_carga_cierre.py --periodo "$PERIODO" --paquete "$BASE/preparados" --plan "$BASE/plan_carga_cierre.json" --estado "$BASE/estado_cierre.json"
"$ROOT/.venv/bin/python" scripts/vincular_evidencia_cierre.py --periodo "$PERIODO" --paquete "$BASE/preparados" --conciliacion "$BASE/conciliacion.json" --plan "$BASE/plan_carga_cierre.json" --estado "$BASE/estado_cierre.json"
echo "PREFLIGHT COMPLETADO, SIN ESCRITURAS NI TRASLADO. CIERRE NO AUTORIZADO."
