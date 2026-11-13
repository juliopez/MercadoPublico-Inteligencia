#!/usr/bin/env bash
# Ubuntu 16:15: solo dispara GitHub Actions, no consulta API ni escribe MER.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export TZ=America/Santiago
HOY="$(date +%F)"
[[ "$(date +%u)" -le 5 && "$(date +%H:%M)" == "16:15" ]] || { echo "FUERA_DE_VENTANA $HOY"; exit 2; }
command -v gh >/dev/null || { echo "BLOQUEO: gh no instalado"; exit 3; }
gh auth status >/dev/null 2>&1 || { echo "BLOQUEO: gh sin autenticacion"; exit 4; }
gh workflow run licitaciones-api-1615-actions.yml --repo juliopez/MercadoPublico-Inteligencia --ref main
echo "DISPATCH_LICITACIONES_1615_OK $HOY $(date --iso-8601=seconds)"
