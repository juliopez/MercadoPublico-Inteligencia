#!/usr/bin/env bash
# Conciliacion cronologica diaria de lunes a viernes a las 09:00 Santiago.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export TZ=America/Santiago
export GOOGLE_APPLICATION_CREDENTIALS="${GOOGLE_APPLICATION_CREDENTIALS:-$HOME/.config/mercadopublico/servicio-google.json}"
mkdir -p logs salida_operativa
exec 9>"$ROOT/logs/.conciliacion_mer_0900.lock"
flock -n 9 || { echo "CONCILIACION_YA_ACTIVA";exit 0; }
exec 8>"$ROOT/logs/.mer_escritura_compartida.lock"
flock -w 3600 8 || { echo "MER_OCUPADO";exit 5; }
[[ -x .venv/bin/python ]] || { echo "FALTA_VENV";exit 2; }
[[ -f "$GOOGLE_APPLICATION_CREDENTIALS" ]] || { echo "FALTA_CREDENCIAL";exit 2; }
[[ -z "$(git status --porcelain --untracked-files=no)" ]] || { echo "GIT_NO_LIMPIO";exit 6; }
git pull --ff-only origin main
.venv/bin/python scripts/conciliar_mer_cronologico.py --aplicar
export MER_CONCILIACION_PERIODOS=1
.venv/bin/python - <<'PY'
import json,os,subprocess
from pathlib import Path
p=Path("salida_operativa/conciliacion_cronologica.json")
r=json.loads(p.read_text())
if r.get("estado") not in ("CONCILIACION_VERIFICADA","CONCILIACION_PARCIAL_VERIFICADA"):
 print("SIN_PUBLICACION: no hubo traslados");raise SystemExit(0)
for periodo in r["periodos_afectados"]:
 subprocess.run([".venv/bin/python","scripts/exportar_mer_operativo_v2.py","--periodo",periodo,"--aplicar","--incluir-api"],check=True)
 print("EXPORTADO_PERIODO",periodo,flush=True)
PY
git add frontend-v2/data/catalogo-publico.json frontend-v2/data/partes/
if git diff --cached --quiet; then echo "SIN_CAMBIOS_GIT";exit 0;fi
git diff --cached --check
git -c user.name="MER Ubuntu Conciliacion" -c user.email="41898282+github-actions[bot]@users.noreply.github.com" commit -m "data(v2): conciliacion cronologica MER"
git push origin main
echo "CONCILIACION_PUBLICADA $(date --iso-8601=seconds)"
