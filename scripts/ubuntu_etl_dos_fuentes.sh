#!/usr/bin/env bash
# ETL Ubuntu restringido a dos ZIP, ejecución serializada y log permanente.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
mkdir -p logs salida_operativa
if [[ ! -x .venv/bin/python ]]; then echo "Ejecuta ubuntu_preparar_prueba.sh primero" >&2; exit 1; fi
MODE="${1:---simular}"
if [[ "$MODE" != "--simular" && "$MODE" != "--aplicar" ]]; then
 echo "Uso: $0 --simular|--aplicar" >&2;exit 2
fi
export TZ=America/Santiago
STAMP="$(date +%Y%m%d_%H%M%S)"
LOG="$ROOT/logs/etl_dos_fuentes_$STAMP.log"
exec 8>"$ROOT/logs/.mer_escritura_compartida.lock"
flock -n 8 || { echo "Bloqueo MER ocupado por cierre u otro escritor; ETL no iniciado"; exit 5; }
exec 9>"$ROOT/logs/.etl_dos_fuentes.lock"
flock -n 9 || { echo "Otra ejecución activa; no se superpone"; exit 3; }
INICIO_EPOCH="$(date +%s)"
echo "INICIO $(date --iso-8601=seconds) MODO=$MODE" | tee "$LOG"
if [[ "$MODE" == "--aplicar" ]]; then
 test -n "${GOOGLE_APPLICATION_CREDENTIALS:-}" && test -r "$GOOGLE_APPLICATION_CREDENTIALS" || { echo "Faltan credenciales Google localmente" | tee -a "$LOG"; exit 4; }
 ARGS=(--aplicar)
else
 ARGS=()
fi
set +e
"$ROOT/.venv/bin/python" scripts/etl_zip_dos_fuentes.py "${ARGS[@]}" --salida "$ROOT/salida_operativa" 2>&1 | tee -a "$LOG"
STATUS=${PIPESTATUS[0]}
set -e
if [[ "$MODE" == "--aplicar" ]]; then
  "$ROOT/.venv/bin/python" scripts/registrar_sincronizacion.py --salida "$ROOT/salida_operativa" --inicio-epoch "$INICIO_EPOCH" --codigo "$STATUS" | tee -a "$LOG" || true
fi
echo "FIN $(date --iso-8601=seconds) CODIGO=$STATUS" | tee -a "$LOG"
exit "$STATUS"
