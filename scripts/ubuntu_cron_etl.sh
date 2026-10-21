#!/usr/bin/env bash
# Programador por hora del reloj de Santiago. SOLO ejecuta lunes-viernes a las 16:00.
# --verificar: comprueba prerrequisitos sin descargar ni escribir datos.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export TZ=America/Santiago
export GOOGLE_APPLICATION_CREDENTIALS="${GOOGLE_APPLICATION_CREDENTIALS:-$HOME/.config/mercadopublico/servicio-google.json}"
MODO="${1:-}"
if [[ "$MODO" != "--verificar" ]]; then
 DIA="$(date +%u)"
 HORA="$(date +%H)"
 if [[ "$DIA" -gt 5 || "$HORA" != "16" ]]; then exit 0; fi
fi
if [[ ! -x "$ROOT/.venv/bin/python" ]]; then
 echo "ERROR: falta entorno Python .venv";exit 2
fi
if [[ ! -r "$GOOGLE_APPLICATION_CREDENTIALS" ]]; then
 echo "ERROR: falta credencial local legible: $GOOGLE_APPLICATION_CREDENTIALS";exit 3
fi
# Condición de seguridad: hoja del mes vigente creada en cuenta del usuario y catalogada.
"$ROOT/.venv/bin/python" - <<'PY'
import datetime,json
from pathlib import Path
from zoneinfo import ZoneInfo
root=Path.cwd()
cat=json.loads((root/"config/catalogo_sheets.json").read_text(encoding="utf-8"))
hoy=datetime.datetime.now(ZoneInfo("America/Santiago"))
mes=hoy.strftime("%Y-%m")
d=cat.get("periodos",{}).get(mes)
if not d or d.get("tipo")!="operativo" or not d.get("id"):
 raise SystemExit("BLOQUEADO: MER operativo del mes "+mes+" no está creado y catalogado.")
print("Destino operativo:",mes,d["id"],flush=True)
if hoy.month==12:proximo=f"{hoy.year+1}-01"
else:proximo=f"{hoy.year}-{hoy.month+1:02d}"
next_entry=cat.get("periodos",{}).get(proximo)
if not next_entry or next_entry.get("tipo")!="operativo":
 print("AVISO: se debe preparar MER_"+proximo.replace("-","_")+"_OPERATIVO antes del día 1.",flush=True)
PY
if [[ "$MODO" == "--verificar" ]]; then
 echo "VERIFICACIÓN CRON OK: sin descargas y sin escrituras."
 exit 0
fi
exec /bin/bash "$ROOT/scripts/ubuntu_etl_dos_fuentes.sh" --aplicar
