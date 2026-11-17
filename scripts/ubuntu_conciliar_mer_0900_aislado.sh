#!/usr/bin/env bash
# P7: ejecucion aislada sin alterar archivos de desarrollo.
set -Eeuo pipefail
DEV_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNTIME="${MER_CONCILIACION_RUNTIME:-$HOME/.local/share/mercadopublico/conciliacion-runtime}"
mkdir -p "$DEV_ROOT/logs"
[[ -x "$DEV_ROOT/.venv/bin/python" ]] || { echo "FALTA_VENV"; exit 2; }
[[ -f "${GOOGLE_APPLICATION_CREDENTIALS:-$HOME/.config/mercadopublico/servicio-google.json}" ]] || { echo "FALTA_CREDENCIAL"; exit 2; }
if [[ ! -d "$RUNTIME/.git" ]]; then
  [[ ! -e "$RUNTIME" ]] || { echo "RUNTIME_NO_VACIO: $RUNTIME"; exit 6; }
  git clone --quiet --branch main --single-branch "$(git -C "$DEV_ROOT" remote get-url origin)" "$RUNTIME"
fi
[[ "$(git -C "$RUNTIME" remote get-url origin)" == "$(git -C "$DEV_ROOT" remote get-url origin)" ]] || { echo "ORIGEN_RUNTIME_INCORRECTO"; exit 6; }
if [[ ! -e "$RUNTIME/.venv" ]]; then ln -s "$DEV_ROOT/.venv" "$RUNTIME/.venv"; fi
[[ "$(readlink -f "$RUNTIME/.venv")" == "$(readlink -f "$DEV_ROOT/.venv")" ]] || { echo "VENV_RUNTIME_INCORRECTO"; exit 6; }
export MER_LOCK_DIR="$DEV_ROOT/logs"
echo "CONCILIACION_RUNTIME_AISLADO $RUNTIME $(date --iso-8601=seconds)"
exec /bin/bash "$RUNTIME/scripts/ubuntu_conciliar_mer_0900.sh"
