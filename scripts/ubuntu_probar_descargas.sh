#!/usr/bin/env bash
# Solo lectura de ChileCompra; produce archivos locales. NO escribe Sheets.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
mkdir -p logs salida_operativa
if [[ ! -x .venv/bin/python ]]; then
  echo "Ejecuta primero: bash scripts/ubuntu_preparar_prueba.sh" >&2
  exit 1
fi
STAMP="$(date +%Y%m%d_%H%M%S)"
LOG="$ROOT/logs/prueba_descargas_$STAMP.log"
# Evitar dos ejecuciones en el mismo ordenador.
exec 9>"$ROOT/logs/.prueba_etl.lock"
if ! flock -n 9; then echo "Existe otra prueba en curso; se omite esta ejecución"; exit 2; fi
echo "Inicio $(date --iso-8601=seconds)" | tee "$LOG"
set +e
"$ROOT/.venv/bin/python" "$ROOT/scripts/simular_mes_operativo.py" --solo-local --salida "$ROOT/salida_operativa" 2>&1 | tee -a "$LOG"
RESULTADO=${PIPESTATUS[0]}
set -e
echo "Finalización $(date --iso-8601=seconds); código $RESULTADO" | tee -a "$LOG"
echo "Log: $LOG"
exit "$RESULTADO"
