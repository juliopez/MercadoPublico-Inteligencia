#!/usr/bin/env bash
# Compra Ágil: cron local independiente del ETL Ubuntu 16h.
set -Eeuo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"
source "${MER_API_ENV_FILE:-$HOME/.config/mercadopublico/api.env}"
: "${CHILECOMPRA_TICKET:?Falta CHILECOMPRA_TICKET}"
if [[ -z "${GOOGLE_SERVICE_ACCOUNT_JSON:-}" && ! -f "${GOOGLE_APPLICATION_CREDENTIALS:-/ruta/inexistente}" ]]; then
  echo "Falta GOOGLE_SERVICE_ACCOUNT_JSON o GOOGLE_APPLICATION_CREDENTIALS" >&2; exit 1
fi
exec 9>"/tmp/mercadopublico-api-$(id -u).lock"
flock -n 9 || { echo "Otra sincronización API local está ejecutándose"; exit 0; }
[[ -z "$(git status --porcelain)" ]] || { echo "Árbol Git con cambios; detener antes de sincronizar" >&2; exit 1; }
git pull --ff-only origin main
python3 -m pip --version >/dev/null
export MER_API_MAX_DETAIL=10
python3 scripts/mer_api_incremental_10.py
python3 - <<'PY'
import json,subprocess
r=json.load(open('control/ultimo_reporte_api_mer.json'))
changed=sum(int(r.get(k,0)) for k in ('procesos','ofertas','resultados','procesos_enriquecidos','ofertas_enriquecidos','resultados_enriquecidos'))
if changed:
 subprocess.run(['python3','scripts/exportar_mer_operativo_v2.py','--periodo',r['periodo'],'--aplicar','--incluir-api'],check=True)
 print('EXPORTACION_API_REALIZADA',changed)
else:
 print('SIN_CAMBIOS_DATOS_API')
PY
git add control/cola_api_mer.json control/ultimo_reporte_api_mer.json frontend-v2/data/
git diff --cached --check
if git diff --cached --quiet; then echo 'SIN_CAMBIOS_GIT'; exit 0; fi
git -c user.name="Observatorio API local" -c user.email="api-local@users.noreply.github.com" commit -m "data(api): sincronización Compra Ágil desde cron Ubuntu"
git pull --rebase origin main
git push origin main
if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
 gh workflow run publicacion-v2-post-etl.yml --ref main
else
 echo 'ATENCION: falta gh autenticado; verificar generación derivada tras push' >&2
fi
