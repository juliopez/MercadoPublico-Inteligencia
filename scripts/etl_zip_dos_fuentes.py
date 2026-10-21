#!/usr/bin/env python3
"""ETL operativo MER v2: ZIP de licitaciones y OC, sin Compra Ágil.
Solo escribe con --aplicar; exige credencial local y respaldo verificable ZIP de las seis pestañas.
"""
import argparse,csv,datetime as dt,hashlib,importlib.util,io,json,os,sqlite3,sys,tempfile,time,random,urllib.request,zipfile
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
ZONE=ZoneInfo("America/Santiago")
EXCLUIDOS={"1y81QaPy37APkBwxlYrKyE66_1ECdhL87GyWNitTfHr4","1loeK_IM3RXHaR7CqpjUbz-TsNgOKNrV1ejq8aRC6JyE"}
def importar():
 spec=importlib.util.spec_from_file_location("historicos_mer",ROOT/"scripts/importador_historicos_v2.py")
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
def descargar(url,path):
 req=urllib.request.Request(url,headers={"User-Agent":"MercadoPublico-MER-v2/1.0"})
 with urllib.request.urlopen(req,timeout=180) as res,open(path,"wb") as out:
  import shutil;shutil.copyfileobj(res,out,1024*1024)
 with zipfile.ZipFile(path) as z:
  if not any(x.filename.lower().endswith(".csv") for x in z.infolist()):raise ValueError("ZIP sin CSV")
  bad=z.testzip()
  if bad:raise ValueError("CRC incorrecto: "+bad)
 return {"url":url,"bytes":path.stat().st_size,"sha256":hashlib.sha256(path.read_bytes()).hexdigest()}
def worksheet_rows(ws,cols):
 vals=ws.get_all_values()
 if not vals or vals[0]!=cols:raise ValueError("Contrato MER incompatible: "+ws.title)
 result={}
 for i,arr in enumerate(vals[1:],start=2):
  if not arr or not arr[0]:continue
  if arr[0] in result:raise ValueError("PK duplicada en destino "+ws.title)
  result[arr[0]]=(i,(arr+[""]*len(cols))[:len(cols)])
 return result
def respaldo_local(book,schemas,periodo):
 """Copia completa verificable de las seis pestañas antes de toda escritura."""
 destino=Path.home()/".local"/"share"/"mercadopublico"/"respaldos"
 destino.mkdir(parents=True,exist_ok=True,mode=0o700)
 os.chmod(destino,0o700)
 ts=dt.datetime.now(ZONE).strftime("%Y%m%d_%H%M%S_%f")
 final=destino/f"MER_{periodo.replace('-','_')}_ANTES_ETL_{ts}.zip"
 temporal=destino/(final.name+".tmp")
 manifest={"periodo":periodo,"spreadsheet_id":book.id,
           "creado_utc":dt.datetime.now(dt.timezone.utc).isoformat(),"tablas":{}}
 try:
  with zipfile.ZipFile(temporal,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
   for tabla,cols in schemas.items():
    ws=book.worksheet(tabla)
    valores=ws.get_all_values()
    if not valores or valores[0]!=cols:
     raise ValueError("Respaldo bloqueado: cabeceras incompatibles en "+tabla)
    # Proteger contra PK duplicadas y filas parcialmente cargadas.
    vistas=set()
    for row in valores[1:]:
     if not row or not row[0]:raise ValueError("Fila sin PK en "+tabla)
     if row[0] in vistas:raise ValueError("PK repetida en respaldo "+tabla)
     vistas.add(row[0])
     if len(row)>len(cols):raise ValueError("Columnas excedentes en "+tabla)
    buf=io.StringIO(newline="")
    wr=csv.writer(buf);wr.writerow(cols)
    for row in valores[1:]:wr.writerow((row+[""]*len(cols))[:len(cols)])
    contenido=buf.getvalue().encode("utf-8-sig")
    archive.writestr(tabla+".csv",contenido)
    manifest["tablas"][tabla]={"registros":len(valores)-1,"sha256":hashlib.sha256(contenido).hexdigest()}
   archive.writestr("manifiesto.json",json.dumps(manifest,ensure_ascii=False,indent=2))
  with zipfile.ZipFile(temporal) as check:
   if check.testzip():raise ValueError("Respaldo ZIP CRC incorrecto")
   m=json.loads(check.read("manifiesto.json"))
   if set(check.namelist())!=({x+".csv" for x in schemas}|{"manifiesto.json"}):
    raise ValueError("Respaldo incompleto")
   for tabla in schemas:
    raw=check.read(tabla+".csv")
    if hashlib.sha256(raw).hexdigest()!=m["tablas"][tabla]["sha256"]:
     raise ValueError("Huella de respaldo inválida: "+tabla)
  os.chmod(temporal,0o600)
  os.replace(temporal,final)
  with final.open("rb") as fh:
   dig=hashlib.sha256()
   for bloque in iter(lambda:fh.read(1048576),b""):dig.update(bloque)
  return {"archivo":str(final),"bytes":final.stat().st_size,
          "sha256":dig.hexdigest(),
          "registros":{k:v["registros"] for k,v in manifest["tablas"].items()}}
 finally:
  if temporal.exists():temporal.unlink()

def load_rows(db,table,cols):
 for pk,raw in db.execute('SELECT pk,fila FROM "'+table+'" ORDER BY pk'):
  row=json.loads(raw)
  if len(row)!=len(cols) or row[0]!=pk:raise ValueError("Contrato origen corrupto")
  yield pk,[str(v or "") for v in row]
def solicitud_con_reintentos(fn,descripcion,max_intentos=9):
 """Reintentos acotados ante 429 y 5xx, con espera exponencial y jitter."""
 from gspread.exceptions import APIError
 for intento in range(max_intentos):
  try:return fn()
  except APIError as e:
   status=getattr(getattr(e,"response",None),"status_code",None)
   if status not in (429,500,502,503,504) or intento==max_intentos-1:raise
   esperar=min(90,12*(2**min(intento,3)))+random.uniform(0,4)
   print(f"Cuota temporal {status} en {descripcion}, espera {esperar:.0f}s ({intento+1}/{max_intentos})",flush=True)
   time.sleep(esperar)

def aplicar_tabla(ws,cols,rows,existing,max_batch=500):
 """Upsert con paquetes moderados y pausa; relectura ante reintento ambiguo."""
 import gspread
 changed=[];novel=[];same=0
 for pk,row in rows:
  old=existing.get(pk)
  if old is None:novel.append(row)
  elif old[1]==row:same+=1
  else:changed.append((old[0],row))
 def colname(n):
  s=""
  while n:n,x=divmod(n-1,26);s=chr(65+x)+s
  return s
 end=colname(len(cols))
 for i in range(0,len(novel),max_batch):
  batch=novel[i:i+max_batch]
  # No repetir un append tras respuesta ambigua; consultar claves actuales.
  def append_seguro():
   keys=ws.col_values(1)
   keys=set(keys[1:])
   pending=[row for row in batch if row[0] not in keys]
   if pending:ws.append_rows(pending,value_input_option="RAW",insert_data_option="INSERT_ROWS")
  solicitud_con_reintentos(append_seguro,f"{ws.title} inserción {i}")
  if (i//max_batch)%8==0:print(ws.title,"avance",min(i+len(batch),len(novel)),"/",len(novel),flush=True)
  time.sleep(1.3)
 for i in range(0,len(changed),max_batch):
  block=changed[i:i+max_batch]
  solicitud_con_reintentos(lambda:ws.batch_update(
   [{"range":f"A{num}:{end}{num}","values":[row]} for num,row in block],
   value_input_option="RAW"),f"{ws.title} actualización {i}")
  time.sleep(1.3)
 return {"nuevos":len(novel),"modificados":len(changed),"sin_cambios":same}
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--aplicar",action="store_true",help="Autoriza escrituras en MER operativo tras preflight y respaldo")
 p.add_argument("--salida",default="salida_operativa")
 p.add_argument("--periodo",help="Solo mes vigente, YYYY-MM")
 args=p.parse_args()
 periodo=dt.datetime.now(ZONE).strftime("%Y-%m")
 if args.periodo and args.periodo!=periodo:p.error("No se permite escribir ni procesar otro mes")
 config=json.loads((ROOT/"config/fuentes_descarga_mensual.json").read_text())
 catalogo=json.loads((ROOT/"config/catalogo_sheets.json").read_text())
 dest=catalogo["periodos"].get(periodo)
 if not dest or dest["tipo"]!="operativo" or dest["id"] in EXCLUIDOS:
  p.error("El mes vigente aún no tiene hoja MER operativa autorizada")
 yy,mm=periodo.split("-")
 url=lambda key:config["fuentes"][key].format(yyyy=yy,mm=mm)
 out=Path(args.salida).resolve();out.mkdir(parents=True,exist_ok=True)
 mod=importar()
 # Preflight temporal: cualquiera de las dos fuentes puede fallar sin afectar la otra.
 # Se preparan ambas antes de cualquier escritura para evitar cortes parciales.
 with tempfile.TemporaryDirectory(prefix="mer_zip_") as temp:
  temp=Path(temp);paths={"licitaciones":temp/f"{periodo}.zip","ordenes_compra":temp/f"{periodo} (OC).zip"}
  fuentes={}
  for k in paths:
   print("DESCARGANDO",k,url(k),flush=True)
   fuentes[k]=descargar(url(k),paths[k])
  db=sqlite3.connect(str(temp/"staging.sqlite"));mod.init(db)
  from collections import Counter
  counts=Counter()
  mod.process_licitaciones(db,paths["licitaciones"],counts)
  mod.process_oc(db,paths["ordenes_compra"],counts)
  db.commit()
  # No llenar COT/Ofertas/Resultados con ceros: fuente ausente no implica cero.
  expected={"Procesos":mod.SCHEMA["Procesos"],"OrdenesCompra":mod.SCHEMA["OrdenesCompra"],"Proveedores":mod.SCHEMA["Proveedores"]}
  for table,cols in expected.items():
   n=db.execute('SELECT COUNT(*) FROM "'+table+'"').fetchone()[0]
   if n<1:raise ValueError("Tabla de fuente inesperadamente vacía: "+table)
  report={"periodo":periodo,"fecha_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
          "modo":"APLICAR" if args.aplicar else "SIMULACION","fuentes":fuentes,
          "preparados":{t:db.execute('SELECT COUNT(*) FROM "'+t+'"').fetchone()[0] for t in expected}}
  if args.aplicar:
   try:
    import gspread
    from google.oauth2.service_account import Credentials
   except ImportError as e:raise RuntimeError("Instala gspread google-auth google-api-python-client") from e
   credfile=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
   if not credfile or not Path(credfile).is_file():raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS no está definido o no existe")
   creds=Credentials.from_service_account_file(credfile,scopes=["https://www.googleapis.com/auth/spreadsheets"])
   gc=gspread.authorize(creds)
   book=gc.open_by_key(dest["id"])
   tables={}
   for table,cols in expected.items():
    ws=book.worksheet(table);current=solicitud_con_reintentos(lambda:worksheet_rows(ws,cols),table+' lectura')
    original=dict(load_rows(db,table,cols))
    newer=sum(key not in current for key in original)
    modified=sum(key in current and current[key][1]!=row for key,row in original.items())
    tables[table]={"existentes":len(current),"nuevos":newer,"modificados":modified}
   report["previo"]=tables
   sheets=book.worksheets()
   projected=sum(x.row_count*x.col_count for x in sheets)
   growth=sum(tables[t]["nuevos"]*len(expected[t]) for t in expected)
   if projected+growth>10_000_000:raise ValueError("Límite de 10 millones de celdas: bloqueada escritura")
   report["respaldo_local"]=respaldo_local(book,mod.SCHEMA,periodo)
   print("RESPALDO LOCAL VERIFICADO:",report["respaldo_local"]["archivo"],flush=True)
   report["aplicados"]={}
   for table,cols in expected.items():
    ws=book.worksheet(table);current=worksheet_rows(ws,cols)
    report["aplicados"][table]=aplicar_tabla(ws,cols,load_rows(db,table,cols),current)
    # Read-back counts and PK integrity
    after=solicitud_con_reintentos(lambda:worksheet_rows(ws,cols),table+' verificacion')
    expected_size=len(current)+report["aplicados"][table]["nuevos"]
    if len(after)!=expected_size:raise ValueError("Verificación de PK falló en "+table)
    for key,row in load_rows(db,table,cols):
     if key not in after or after[key][1]!=row:
      raise ValueError("Verificación de contenido falló en "+table+" PK "+key)
   report["estado"]="CARGA_VERIFICADA"
  else:
   report["estado"]="PREPARADO_SIN_ESCRITURAS"
  location=out/f"etl_zip_operativo_{periodo}.json"
  location.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf8")
  print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
  print("INFORME",location,flush=True)
  db.close()
if __name__=="__main__":main()
