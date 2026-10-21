#!/usr/bin/env python3
"""Cierre mensual MER v2: descarga y prepara paquete oficial; NO escribe ni archiva.

Ejecución prevista desde el día 10, período anterior, zona America/Santiago.
Pasos verificables e idempotentes: DESCARGA -> IMPORTACION -> REVISION.
El cierre definitivo requiere conciliación y auditoría independientes.
"""
import argparse,datetime as dt,hashlib,json,os,subprocess,sys,tempfile,zipfile
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
TZ=ZoneInfo("America/Santiago")
TIPOS={"licitaciones":"licitaciones","cot":"compra_agil","oc":"ordenes_compra"}
def sha256(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
 return h.hexdigest()
def guardar(p,obj):
 p.parent.mkdir(parents=True,exist_ok=True)
 fd,tmp=tempfile.mkstemp(prefix=".cierre_",dir=p.parent)
 try:
  with os.fdopen(fd,"w",encoding="utf-8") as f:
   json.dump(obj,f,ensure_ascii=False,indent=2);f.write("\n");f.flush();os.fsync(f.fileno())
  os.replace(tmp,p)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
def descarga(url, destino):
 # Reusar downloader operativo (CRC, al menos un CSV y SHA-256).
 from etl_zip_dos_fuentes import descargar
 meta=descargar(url,destino)
 with zipfile.ZipFile(destino) as z:
  bad=z.testzip()
  if bad:raise RuntimeError("CRC incorrecto: "+bad)
 return meta
def main():
 p=argparse.ArgumentParser(description="Preparar cierre histórico mensual con tres ZIP; sin escritura")
 p.add_argument("--periodo",help="AAAA-MM (solo mes anterior)")
 p.add_argument("--desde-dia",type=int,default=10)
 p.add_argument("--directorio",default=str(Path.home()/".local/share/mercadopublico/cierres"))
 args=p.parse_args()
 now=dt.datetime.now(TZ);first=now.date().replace(day=1)
 prev=(first-dt.timedelta(days=1)).strftime("%Y-%m")
 if args.periodo and args.periodo!=prev:p.error("Cierre solo del mes anterior: "+prev)
 if now.day<args.desde_dia:p.error("Cierre no habilitado antes del día "+str(args.desde_dia))
 month=prev
 cat=json.loads((ROOT/"config/catalogo_sheets.json").read_text(encoding="utf8"))
 src=cat["periodos"].get(month)
 if not src or src.get("tipo")!="operativo" or not src.get("id"):p.error("Mes anterior no es operativo catalogado")
 cur=cat["periodos"].get(now.strftime("%Y-%m"))
 if not cur or cur.get("tipo")!="operativo" or not cur.get("id"):p.error("Falta mes operativo vigente")
 banned=set(cat.get("excluidos",{}).values())
 if src["id"] in banned or src["id"]==cur["id"]:p.error("Destino inseguro")
 cfg=json.loads((ROOT/"config/fuentes_descarga_mensual.json").read_text(encoding="utf8"))
 yy,mm=month.split("-")
 root=Path(args.directorio).expanduser().resolve()/month
 root.mkdir(parents=True,exist_ok=True)
 estado=root/"estado_cierre.json"
 prevstate=json.loads(estado.read_text(encoding="utf8")) if estado.exists() else {}
 status={"periodo":month,"ejecutado_chile":now.isoformat(),"estado":"DESCARGANDO",
         "hoja_operativa_origen":src["id"],"hoja_vigente_no_afectada":cur["id"],
         "descargas":{},"escrituras_google":False,"traslado_drive":False,
         "catalogo_actualizado":False}
 if prevstate.get("estado")=="LISTO_PARA_CONCILIAR":
  good=True
  for data in prevstate.get("descargas",{}).values():
   f=Path(data["archivo"])
   if not f.is_file() or sha256(f)!=data["sha256"]:good=False;break
  if good and (root/"preparados/informe.json").exists():
   print("PAQUETE YA PREPARADO:",root)
   print("Pendiente: conciliación, auditoría y aprobación de cierre; no se traslada.")
   return
 guardar(estado,status)
 try:
  files={"licitaciones":root/f"{month}.zip","cot":root/f"COT_{month}.zip","oc":root/f"{month} (OC).zip"}
  for typ,key in TIPOS.items():
   f=files[typ]
   url=cfg["fuentes"][key].format(yyyy=yy,mm=mm)
   # Conservar descargas verificadas; reintentar solo las faltantes o dañadas.
   old=prevstate.get("descargas",{}).get(typ,{})
   if f.is_file() and old.get("sha256")==sha256(f) and old.get("url")==url:
    meta=old.copy()
   else:
    partial=f.with_suffix(f.suffix+".partial")
    try:
     meta=descarga(url,partial)
     os.replace(partial,f)
    finally:
     if partial.exists():partial.unlink()
    meta["archivo"]=str(f)
   status["descargas"][typ]=meta
   guardar(estado,status)
  status["estado"]="IMPORTANDO"
  guardar(estado,status)
  prepar=root/"preparados"
  prepar.mkdir(exist_ok=True)
  # Importador estándar histórico produce seis CSV + SQLite + informe.
  cmd=[sys.executable,str(ROOT/"scripts/importador_historicos_v2.py"),
       "--licitaciones",str(files["licitaciones"]),"--cot",str(files["cot"]),
       "--oc",str(files["oc"]),"--out",str(prepar),"--anio",yy,"--mes",str(int(mm))]
  if (prepar/"preparado.sqlite").exists(): (prepar/"preparado.sqlite").unlink()
  subprocess.run(cmd,check=True)
  report=json.loads((prepar/"informe.json").read_text(encoding="utf8"))
  if report.get("periodo")!=month or report.get("validacion_filas")!="OK":
   raise ValueError("Validación de paquete insuficiente")
  names=["Procesos","Ofertas","Resultados","OrdenesCompra","Proveedores","VinculosCOT_OC"]
  for name in names:
   if name not in report or not (prepar/(name+".csv")).is_file():
    raise ValueError("Falta tabla o conteo: "+name)
  status["conteos"]={t:report[t] for t in names}
  status["observaciones"]={k:v for k,v in report.items() if k.endswith("_sin_proceso") or k=="selecciones_ambiguas"}
  status["estado"]="LISTO_PARA_CONCILIAR"
  guardar(estado,status)
  print("PAQUETE PREPARADO",month,root)
  print("NO se ha escrito en Sheets, NO se ha movido ningún archivo.")
  print("PRÓXIMO CONTROL: conciliar con hoja operativa, auditoría aprobada y respaldo.")
 except Exception as e:
  status["estado"]="BLOQUEADO"
  status["motivo"]=str(e)
  guardar(estado,status)
  raise
if __name__=="__main__":main()
