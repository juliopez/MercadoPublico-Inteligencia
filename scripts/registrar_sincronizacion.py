#!/usr/bin/env python3
"""Bitácora LOCAL de sincronización. Nunca escribe Google Sheets ni frontend."""
import argparse,datetime as dt,json,os,tempfile
from pathlib import Path
from zoneinfo import ZoneInfo
CHILE=ZoneInfo("America/Santiago")
def guardar_atomico(path,obj):
 path.parent.mkdir(parents=True,exist_ok=True)
 fd,tmp=tempfile.mkstemp(prefix=".estado_",suffix=".tmp",dir=path.parent)
 try:
  with os.fdopen(fd,"w",encoding="utf-8") as f:
   json.dump(obj,f,ensure_ascii=False,indent=2);f.write("\n");f.flush();os.fsync(f.fileno())
  os.replace(tmp,path)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--salida",required=True)
 p.add_argument("--inicio-epoch",required=True,type=int)
 p.add_argument("--codigo",required=True,type=int)
 args=p.parse_args()
 folder=Path(args.salida)
 now=dt.datetime.now(CHILE)
 period=dt.datetime.fromtimestamp(args.inicio_epoch,CHILE).strftime("%Y-%m")
 reportfile=folder/f"etl_zip_operativo_{period}.json"
 report=None
 if reportfile.is_file():
  candidate=json.loads(reportfile.read_text(encoding="utf-8"))
  timestamp=dt.datetime.fromisoformat(candidate["fecha_utc"]).timestamp()
  if timestamp>=args.inicio_epoch-2 and candidate.get("periodo")==period:report=candidate
 ok=args.codigo==0 and report is not None and report.get("estado")=="CARGA_VERIFICADA" and report.get("modo")=="APLICAR"
 statefile=folder/"estado_sincronizacion.json"
 previous=json.loads(statefile.read_text(encoding="utf-8")) if statefile.exists() else {}
 item={"periodo":period,"ejecucion_chile":now.isoformat(),"codigo_salida":args.codigo,
       "estado":"EXITOSA" if ok else "FALLIDA",
       "error":None if ok else "Revisar logs/etl_dos_fuentes; carga incompleta o informe ausente",
       "fuentes":{}}
 if ok:
  for k in ("licitaciones","ordenes_compra"):
   item["fuentes"][k]={"url":report["fuentes"][k]["url"],"sha256":report["fuentes"][k]["sha256"],
                       "descarga_verificada_chile":now.isoformat()}
  item["tablas"]=report.get("aplicados",{})
 historyfile=folder/"historial_sincronizacion.jsonl"
 historyfile.parent.mkdir(parents=True,exist_ok=True)
 with historyfile.open("a",encoding="utf-8") as f:
  f.write(json.dumps(item,ensure_ascii=False)+"\n")
 result={"ultima_ejecucion":item,
         "ultima_sincronizacion_exitosa":item if ok else previous.get("ultima_sincronizacion_exitosa"),
         "compra_agil":{"estado":"FUENTE_INDEPENDIENTE_NO_ACTUALIZADA_POR_ESTE_ETL"}}
 guardar_atomico(statefile,result)
 print("CONTROL_SINCRONIZACION:",item["estado"],statefile,flush=True)
if __name__=="__main__":main()
