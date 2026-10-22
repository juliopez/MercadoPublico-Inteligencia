#!/usr/bin/env bash
# Coordinación diaria; sin cambio de horario. No sustituye código ETL validado.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export TZ=America/Santiago
export GOOGLE_APPLICATION_CREDENTIALS="${GOOGLE_APPLICATION_CREDENTIALS:-$HOME/.config/mercadopublico/servicio-google.json}"
MODE="${1:---verificar}"
if [[ "$MODE" != --verificar && "$MODE" != --cron && "$MODE" != --ejecutar ]]; then
  echo "Uso: $0 --verificar|--cron|--ejecutar" >&2; exit 2
fi
if [[ "$MODE" == --cron ]]; then
  [[ "$(date +%u)" -le 5 && "$(date +%H)" == 16 ]] || exit 0
fi
# --verificar es totalmente no destructivo; no dispara ETL ni descarga.
bash "$ROOT/scripts/ubuntu_cron_etl.sh" --verificar
for f in "$ROOT/scripts/ubuntu_etl_dos_fuentes.sh" "$ROOT/scripts/etl_conciliacion_cot_oc.py" "$ROOT/scripts/registrar_sincronizacion.py"; do
  [[ -f "$f" ]] || { echo "Falta $f" >&2;exit 3; }
done
"$ROOT/.venv/bin/python" -m py_compile "$ROOT/scripts/etl_conciliacion_cot_oc.py" "$ROOT/scripts/importador_historicos_v2.py" "$ROOT/scripts/exportar_mer_operativo_v2.py" "$ROOT/scripts/completar_montos_operativos.py"
# Prevenir nuevas cargas con el mapeo de licitaciones anterior al arreglo del 22/10.
"$ROOT/.venv/bin/python" - <<'PY'
import importlib.util,pathlib
path=pathlib.Path("scripts/importador_historicos_v2.py")
spec=importlib.util.spec_from_file_location("mer_importador",path)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
assert callable(getattr(mod,"monto_presupuesto_clp",None)), "Importador desactualizado: falta mapeo de presupuesto CLP visible"
assert mod.monto_presupuesto_clp({"CodigoMoneda":"CLP","Estimacion":"1","VisibilidadMonto":"1","MontoEstimado":"1234"})=="1234"
assert mod.monto_presupuesto_clp({"CodigoMoneda":"USD","Estimacion":"1","VisibilidadMonto":"1","MontoEstimado":"1234"})==""
assert mod.monto_presupuesto_clp({"CodigoMoneda":"CLP","Estimacion":"2","VisibilidadMonto":"1","MontoEstimado":"1234"})==""
print("MAPEO_PRESUPUESTO_CLP_VERIFICADO")
PY
if [[ "$MODE" == --verificar ]]; then
  echo "INTEGRACION_VERIFICADA: sin descargas ni escrituras; cron no modificado"
  exit 0
fi
mkdir -p logs salida_operativa
# Candado de orquestación distinto al lock de escritura interno del ETL y conciliador.
exec 7>"$ROOT/logs/.orquestacion_diaria.lock"
flock -n 7 || { echo "Ya hay una orquestación activa" >&2;exit 5; }
MES="$(date +%Y-%m)"
STAMP="$(date +%Y%m%d_%H%M%S)"
LOG="$ROOT/logs/orquestador_integrado_${STAMP}.log"
exec > >(tee -a "$LOG") 2>&1
export MES
printf 'ORQUESTADOR inicio=%s periodo=%s\n' "$(date --iso-8601=seconds)" "$MES"
STATUS_FILE="$ROOT/salida_operativa/estado_conciliacion.json"
write_status() {
  local estado="$1" razon="$2"; export ESTADO_CONC="$estado" RAZON_CONC="$razon" STATUS_FILE
  "$ROOT/.venv/bin/python" - <<'PY'
import os,json,tempfile,datetime
from pathlib import Path
p=Path(os.environ['STATUS_FILE']);p.parent.mkdir(parents=True,exist_ok=True)
old=json.loads(p.read_text()) if p.exists() else {}
new={'periodo':os.environ['MES'],'momento':datetime.datetime.now(datetime.timezone.utc).isoformat(),
     'estado':os.environ['ESTADO_CONC'],'motivo':os.environ['RAZON_CONC']}
old['ultima_ejecucion']=new
if new['estado']=='CONCILIACION_VERIFICADA':old['ultima_conciliacion_exitosa']=new
fd,tmp=tempfile.mkstemp(dir=p.parent,prefix='.estado_conc_',suffix='.tmp')
with os.fdopen(fd,'w') as f:
 json.dump(old,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
os.replace(tmp,p)
PY
}
# El ejecutor original mantiene su propia bitácora y candado de escritura.
if ! bash "$ROOT/scripts/ubuntu_etl_dos_fuentes.sh" --aplicar; then
  write_status OMITIDA "ETL principal fallido: conciliacion no ejecutada"
  echo 'ERROR: etapa principal. No se inicia conciliación.' >&2;exit 10
fi
# Exigir evidencia fresca de éxito en esta ejecución: la etapa principal ya marcó éxito.
if ! "$ROOT/.venv/bin/python" - <<'PY'
import json,datetime,os
from pathlib import Path
p=Path('salida_operativa/estado_sincronizacion.json')
r=json.loads(p.read_text())['ultima_ejecucion']
assert r['periodo']==os.environ['MES'] and r['estado']=='EXITOSA' and r['codigo_salida']==0
assert (datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(r['ejecucion_chile'])).total_seconds()<3600
PY
then
  write_status OMITIDA 'Falta certificacion del ETL principal'
  exit 11
fi
# Publicar solamente tras carga de Sheets verificada; la publicación es independiente
# del estado de éxito del ETL y deja log propio en el orquestador.
publicar_v2() {
  if ! bash "$ROOT/scripts/ubuntu_publicar_v2_post_etl.sh" --aplicar; then
    echo 'PUBLICACION_V2_FALLIDA: Sheets fue actualizada; revisar GitHub y reintentar de forma controlada' >&2
    return 20
  fi
  echo 'PUBLICACION_V2_OK_O_SIN_CAMBIOS'
}
# Descarga SOLO OC vigente, no COT diario; se cachea por mes.
OC_PATH="$ROOT/salida_operativa/cache_oc/${MES}.zip"
mkdir -p "$(dirname "$OC_PATH")"
export OC_PATH
if ! "$ROOT/.venv/bin/python" "$ROOT/scripts/descargar_oc_incremental.py" "$MES" "$OC_PATH"; then
  write_status FALLIDA 'No fue posible verificar el ZIP OC de la conciliacion'
  exit 12
fi
# Huella del ZIP: evitar hacer de nuevo conciliaciones verificadas para un ZIP sin cambios.
HASH="$(sha256sum "$OC_PATH" | cut -d' ' -f1)"
HASHFILE="$ROOT/salida_operativa/cache_oc/${MES}.conciliado.sha256"
if [[ -f "$HASHFILE" && "$(cat "$HASHFILE")" == "$HASH" ]]; then
  write_status CONCILIACION_VERIFICADA 'ZIP OC sin cambios; conciliacion verificada anteriormente'
  echo 'CONCILIACION omitida: SHA256 idéntico y verificado'
  publicar_v2
  exit 0
fi
# El conciliador gestiona el lock compartido, respaldo y lectura posterior.
if ! "$ROOT/.venv/bin/python" "$ROOT/scripts/etl_conciliacion_cot_oc.py" --oc "$OC_PATH" --periodo "$MES" --aplicar --salida "$ROOT/salida_operativa"; then
  write_status FALLIDA 'Conciliacion no concluida; revisar posibles escrituras parciales'
  exit 13
fi
if ! "$ROOT/.venv/bin/python" - <<'PY'
import json,os
from pathlib import Path
r=json.loads((Path('salida_operativa')/('conciliacion_cot_oc_'+os.environ['MES']+'.json')).read_text())
assert r['estado']=='CONCILIACION_VERIFICADA' and r['modo']=='APLICAR'
assert r['nuevos_confirmados']==r['nuevos_a_insertar']
PY
then
  write_status FALLIDA 'Informe de conciliacion no verifica los registros'
  exit 14
fi
printf '%s\n' "$HASH" > "$HASHFILE.tmp"
mv -f "$HASHFILE.tmp" "$HASHFILE"
write_status CONCILIACION_VERIFICADA 'Conciliacion y lectura posterior verificadas'
publicar_v2
echo "ORQUESTADOR OK: $(date --iso-8601=seconds)"
