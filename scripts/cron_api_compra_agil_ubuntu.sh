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
mkdir -p "$REPO/logs"
exec 8>"$REPO/logs/.mer_escritura_compartida.lock"
flock -n 8 || { echo "MER ocupado por ETL Ubuntu o conciliación; API omitida sin consultas"; exit 0; }
[[ -z "$(git status --porcelain --untracked-files=no)" ]] || { echo "Archivos versionados con cambios; detener para evitar sobrescritura" >&2; exit 1; }
# logs/, salida_operativa/ y scripts locales no versionados permanecen intactos.
git pull --ff-only origin main
[[ -x "$REPO/.venv/bin/python" ]] || { echo "Falta .venv local validado" >&2; exit 1; }
"$REPO/.venv/bin/python" -c "import gspread, google.auth"
# 'auto' solo habilita el mes actual ya archivado, aún pendiente de conciliación.
# En el primer día del nuevo mes se desactiva automáticamente y usa el operativo.
if [[ "${MER_API_CIERRE_EXCEPCIONAL:-}" == "auto" ]]; then
  MER_API_CIERRE_EXCEPCIONAL="$("$REPO/.venv/bin/python" - <<'PY'
import datetime,json,pathlib
from zoneinfo import ZoneInfo
p=datetime.datetime.now(ZoneInfo("America/Santiago")).strftime("%Y-%m")
cat=json.loads(pathlib.Path("config/catalogo_sheets.json").read_text())["periodos"]
entry=cat.get(p,{})
print(p if entry.get("tipo")=="historico" and entry.get("estado")=="cierre_operativo_pendiente_conciliacion_oficial" else "")
PY
)"
  export MER_API_CIERRE_EXCEPCIONAL
fi
export MER_API_MAX_DETAIL="${MER_API_MAX_DETAIL:-100}"
export MER_API_DELAY_SECONDS="${MER_API_DELAY_SECONDS:-10}"
export MER_API_RUN_NOW=1
export MER_API_RUN_ID="$(date +%s%N)-$"
# Solo ejecución local manual o timer autorizado.
"$REPO/.venv/bin/python" scripts/mer_api_incremental_10.py
"$REPO/.venv/bin/python" - <<'PY'
import json,subprocess,datetime,os
from zoneinfo import ZoneInfo
r=json.load(open('control/ultimo_reporte_api_mer.json'))
changed=sum(int(r.get(k,0)) for k in ('procesos','ofertas','resultados','procesos_enriquecidos','ofertas_enriquecidos','resultados_enriquecidos'))
if r.get('id_ejecucion') != os.environ['MER_API_RUN_ID']:
 print('SIN_PUBLICACION: API omitida o informe no pertenece a esta ejecución')
 raise SystemExit(0)
if r.get('fecha') != datetime.datetime.now(ZoneInfo('America/Santiago')).date().isoformat():
 raise SystemExit('BLOQUEO: reporte API anterior a esta ejecución')
if changed:
 subprocess.run(['.venv/bin/python','scripts/exportar_mer_operativo_v2.py','--periodo',r['periodo'],'--aplicar','--incluir-api'],check=True)
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
# El push de catalogo-publico.json dispara automaticamente publicacion-v2-post-etl.yml.
# No enviar workflow_dispatch adicional: duplicaba ejecuciones y generaba conflictos de rebase.
echo "PUBLICACION_DERIVADA_ACTIVADA_POR_PUSH; verificar resultado en Actions"
