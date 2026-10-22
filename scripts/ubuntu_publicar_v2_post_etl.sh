#!/usr/bin/env bash
# Publicación pública posterior a una carga MER verificada. No escribe Sheets.
# Se ejecuta manualmente hasta validar el primer ciclo completo.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export TZ=America/Santiago
export GOOGLE_APPLICATION_CREDENTIALS="${GOOGLE_APPLICATION_CREDENTIALS:-$HOME/.config/mercadopublico/servicio-google.json}"
MES="$(date +%Y-%m)"
if [[ "${1:-}" != "--aplicar" ]]; then
  echo "Modo de simulación: no publica en GitHub"
  "$ROOT/.venv/bin/python" scripts/exportar_mer_operativo_v2.py --periodo "$MES"
  exit 0
fi
"$ROOT/.venv/bin/python" - <<'PY'
import datetime,json
from pathlib import Path
from zoneinfo import ZoneInfo
now=datetime.datetime.now(ZoneInfo("America/Santiago"))
state=json.loads(Path("salida_operativa/estado_sincronizacion.json").read_text())
run=state["ultima_ejecucion"]
stamp=datetime.datetime.fromisoformat(run["ejecucion_chile"])
if run["estado"]!="EXITOSA" or stamp.date()!=now.date() or stamp.hour<16:
 raise SystemExit("BLOQUEADO: falta carga MER verificada posterior a las 16:00")
PY
exec 7>"$ROOT/logs/.publicacion_v2.lock"
flock -n 7 || { echo "Otra publicación V2 está en curso";exit 5; }
test -z "$(git status --porcelain --untracked-files=no)" || {
 echo "BLOQUEADO: cambios locales rastreados, conservar para revisión";exit 6;
}
git pull --ff-only origin main
"$ROOT/.venv/bin/python" scripts/exportar_mer_operativo_v2.py --periodo "$MES" --aplicar
git add frontend-v2/data/catalogo-publico.json "frontend-v2/data/partes/procesos/$MES" "frontend-v2/data/partes/ordenescompra/$MES"
# Eliminar fragmentos antiguos del índice, cuando corresponda
git add -u "frontend-v2/data/partes/procesos/$MES" "frontend-v2/data/partes/ordenescompra/$MES"
if git diff --cached --quiet; then
 echo "SIN_CAMBIOS_PUBLICOS"; exit 0
fi
git diff --cached --check
git -c user.name="MER Ubuntu Publisher" -c user.email="41898282+github-actions[bot]@users.noreply.github.com" commit -m "data(v2): actualizar MER operativo $MES"
git push origin main
echo "CATALOGO_PUBLICO_ACTUALIZADO: GitHub Actions regenerará derivados a las 17:00 Santiago"
