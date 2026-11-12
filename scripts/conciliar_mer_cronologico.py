#!/usr/bin/env python3
"""Conciliacion cronologica MER: fecha propia, escritura-verificacion-borrado.
Lunes-viernes desde Ubuntu. Proveedores y VinculosCOT_OC no se mueven sin fecha propia.
"""
import argparse,datetime as dt,importlib.util,json,os,sys
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
TABLE_DATE={"Procesos":"fecha_publicacion","OrdenesCompra":"fecha_creacion","Ofertas":"fecha_oferta","Resultados":"fecha_resultado"}
def load_mod():
 spec=importlib.util.spec_from_file_location("etl",ROOT/"scripts/etl_zip_dos_fuentes.py")
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
def period(value):
 s=str(value or "").strip()
 if not s:return None
 import re
 m=re.match(r"^(\d{4})[-/](\d{1,2})[-/](\d{1,2})(?:[T\s].*)?$",s)
 if m:
  try:return dt.date(*map(int,m.groups())).strftime("%Y-%m")
  except ValueError:return None
 m=re.match(r"^(\d{1,2})[-/](\d{1,2})[-/](\d{4})(?:[T\s].*)?$",s)
 if m:
  d,mo,y=map(int,m.groups())
  try:return dt.date(y,mo,d).strftime("%Y-%m")
  except ValueError:return None
 return None
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--aplicar",action="store_true")
 a=p.parse_args()
 now=dt.datetime.now(ZoneInfo("America/Santiago"))
 mes=now.strftime("%Y-%m")
 cat=json.loads((ROOT/"config/catalogo_sheets.json").read_text())["periodos"]
 if cat.get(mes,{}).get("tipo")!="operativo":raise RuntimeError("MER operativo no autorizado")
 import gspread
 from google.oauth2.service_account import Credentials
 cred=Path(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS",str(Path.home()/".config/mercadopublico/servicio-google.json")))
 if not cred.is_file():raise RuntimeError("Credencial Google no disponible")
 gc=gspread.authorize(Credentials.from_service_account_file(str(cred),scopes=["https://www.googleapis.com/auth/spreadsheets"]))
 mod=load_mod(); schema=mod.importar().SCHEMA
 # Limitar reintentos solo para esta conciliacion, sin alterar el ETL compartido.
 original_retry=mod.solicitud_con_reintentos
 def retry_acotado(fn,descripcion,max_intentos=3):
  return original_retry(fn,descripcion,max_intentos=min(max_intentos,3))
 mod.solicitud_con_reintentos=retry_acotado
 limite=now.replace(hour=14,minute=0,second=0,microsecond=0)
 def fuera_de_horario():
  return dt.datetime.now(ZoneInfo("America/Santiago"))>=limite
 source=gc.open_by_key(cat[mes]["id"])
 movements={};skipped={};rows_cache={}
 for table,col in TABLE_DATE.items():
  cols=schema[table]
  ws=source.worksheet(table)
  existing=mod.solicitud_con_reintentos(lambda:mod.worksheet_rows(ws,cols),table+" origen")
  rows_cache[table]=existing
  for pk,(number,row) in existing.items():
   dest=period(row[cols.index(col)])
   if dest is None:
    skipped[table]=skipped.get(table,0)+1;continue
   if dest==mes:continue
   if dest not in cat or cat[dest].get("tipo")!="historico":
    skipped[table]=skipped.get(table,0)+1;continue
   movements.setdefault(dest,{}).setdefault(table,[]).append((pk,number,row))
 report={"ejecucion":now.isoformat(),"operativo":mes,"movimientos":{k:{t:len(v) for t,v in x.items()} for k,x in movements.items()},"sin_fecha_o_destino":skipped,"sin_traslado":["Proveedores","VinculosCOT_OC"],"estado":"SIMULACION"}
 out=ROOT/"salida_operativa"/"conciliacion_cronologica.json";out.parent.mkdir(exist_ok=True)
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False))
 print("PLAN_CONCILIACION",json.dumps(report,ensure_ascii=False),flush=True)
 if not a.aplicar:return
 if not movements:
  print("SIN_TRASLADOS");return
 # Bloqueo si hay registros dependientes en el operativo cuya entidad principal saldria:
 # las relaciones cruzadas son validas y se preservan por codigo; nunca se borran catalogos.
 # Respaldo completo origen + cada destino antes de escribir.
 books={mes:source}
 for dest in sorted(movements):
  books[dest]=gc.open_by_key(cat[dest]["id"])
 for name,book in books.items():
  b=mod.respaldo_local(book,schema,name)
  print("RESPALDO_VERIFICADO",name,b["archivo"],flush=True)
 affected=[]
 parcial=False
 for dest,tables in sorted(movements.items()):
  book=books[dest]
  for table,records in tables.items():
   if fuera_de_horario():
    print("LIMITE_1400: no iniciar nueva tabla; traslado parcial verificable",flush=True)
    parcial=True
    break
   cols=schema[table];ws=book.worksheet(table)
   existing=mod.solicitud_con_reintentos(lambda:mod.worksheet_rows(ws,cols),table+" destino "+dest)
   # No reemplazar un registro historico existente: preservar enriquecimientos.
   additions=[(pk,row) for pk,_,row in records if pk not in existing]
   if additions:
    mod.aplicar_tabla(ws,cols,additions,existing)
   after=mod.solicitud_con_reintentos(lambda:mod.worksheet_rows(ws,cols),table+" lectura posterior "+dest)
   for pk,_,row in records:
    if pk not in after:raise RuntimeError("Fallo verificacion destino "+dest+"/"+table+"/"+pk)
    if pk not in existing and after[pk][1]!=row:raise RuntimeError("Fallo contenido destino "+dest+"/"+table+"/"+pk)
   # Eliminar solo las filas verificadas; indices descendentes para no desplazar posiciones.
   originws=source.worksheet(table)
   current=mod.solicitud_con_reintentos(lambda:mod.worksheet_rows(originws,cols),table+" relectura origen")
   numbers=[]
   for pk,_,row in records:
    if pk not in current or current[pk][1]!=row:
     raise RuntimeError("Origen modificado durante conciliacion: "+pk)
    numbers.append(current[pk][0])
   # Reducir solicitudes Sheets: agrupar filas contiguas y enviar hasta 50
   # eliminaciones descendentes por batchUpdate. Cada bloque se reintenta
   # como unidad solo cuando Google confirma que no lo aplico; ante un error
   # ambiguo, detener para evitar borrar filas desplazadas.
   ordenados=sorted(set(numbers),reverse=True)
   rangos=[]
   for number in ordenados:
    if rangos and number==rangos[-1][0]-1:
     rangos[-1]=(number,rangos[-1][1])
    else:
     rangos.append((number,number))
   for offset in range(0,len(rangos),50):
    bloque=rangos[offset:offset+50]
    solicitudes=[{"deleteDimension":{"range":{"sheetId":originws.id,
      "dimension":"ROWS","startIndex":inicio-1,"endIndex":fin}}}
      for inicio,fin in bloque]
    # Una llamada para hasta 50 rangos, en orden descendente.
    source.batch_update({"requests":solicitudes})
    print("RETIRO_LOTE",dest,table,offset//50+1,len(bloque),flush=True)
   check=mod.solicitud_con_reintentos(lambda:mod.worksheet_rows(originws,cols),table+" verificar retiro")
   if any(pk in check for pk,_,_ in records):raise RuntimeError("Retiro no verificado "+dest+"/"+table)
   print("TRASLADO_VERIFICADO",dest,table,len(records),flush=True)
  affected.append(dest)
  if parcial:break
 report["estado"]="CONCILIACION_PARCIAL_VERIFICADA" if parcial else "CONCILIACION_VERIFICADA"
 report["periodos_afectados"]=[mes]+affected
 out.write_text(json.dumps(report,indent=2,ensure_ascii=False))
 print("CONCILIACION_FINALIZADA",json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
