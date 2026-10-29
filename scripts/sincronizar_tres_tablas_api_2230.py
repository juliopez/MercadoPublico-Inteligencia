#!/usr/bin/env python3
"""Micro-lote nocturno Compra Ágil → Procesos, Ofertas, Resultados del MER operativo.
Fail-closed: requiere secreto de servicio autorizado. No modifica ETL de las 16:00.
"""
import datetime as dt,json,os,tempfile,time,urllib.error,urllib.parse,urllib.request
from zoneinfo import ZoneInfo
from adaptar_detalle_compra_agil_mer import adaptar_detalle,OFERTAS,RESULTADOS
from importador_historicos_v2 import SCHEMA

def main():
 import gspread
 from google.oauth2.service_account import Credentials
 now=dt.datetime.now(ZoneInfo("America/Santiago"))
 if now.hour!=22 or not 25<=now.minute<=55 or now.weekday()>4:
  print("SKIP fuera de ventana Chile 22:25-22:55 lunes-viernes");return
 ticket=os.getenv("CHILECOMPRA_TICKET","").strip()
 credential=os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON","").strip()
 credential_file=os.getenv("GOOGLE_APPLICATION_CREDENTIALS","").strip()
 if not ticket or not (credential or credential_file):
  raise SystemExit("BLOQUEADO: falta ticket o identidad Google existente")
 limits=int(os.getenv("MER_API_MAX_DETAIL","2"))
 if limits<1 or limits>5:raise SystemExit("BLOQUEADO: límite inválido")
 if credential_file:
  creds=Credentials.from_service_account_file(credential_file,scopes=["https://www.googleapis.com/auth/spreadsheets"])
 else:
  creds=Credentials.from_service_account_info(json.loads(credential),scopes=["https://www.googleapis.com/auth/spreadsheets"])
 cat=json.load(open("config/catalogo_sheets.json",encoding="utf8"))
 period=now.strftime("%Y-%m")
 target=cat["periodos"].get(period)
 if not target or target.get("tipo")!="operativo":raise SystemExit("BLOQUEADO: no hay MER operativo")
 book=gspread.authorize(creds).open_by_key(target["id"])
 sheets={name:book.worksheet(name) for name in ("Procesos","Ofertas","Resultados")}
 snap={name:sheets[name].get_all_values() for name in sheets}
 for name in sheets:
  if not snap[name] or snap[name][0]!=SCHEMA[name]:raise SystemExit("BLOQUEADO: cabecera incompatible "+name)
 existing={"Procesos":{r[0] for r in snap["Procesos"][1:] if r},
 "Ofertas":{(r[1],r[0]) for r in snap["Ofertas"][1:] if len(r)>1},
 "Resultados":{(r[0],r[1]) for r in snap["Resultados"][1:] if len(r)>1}}
 # Primera ventana observa una página de 10 registros publicados en día local actual.
 headers={"ticket":ticket,"Accept":"application/json","User-Agent":"MER-incremental-nocturno/1"}
 def get(url):
  with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=30) as response:
   raw=response.read(1500001)
   if len(raw)>1500000:raise ValueError("respuesta demasiado grande")
   return json.loads(raw)
 # Recorrer una página del día anterior, para evitar que todos los procesos sigan abiertos.
 day=(now-dt.timedelta(days=1)).strftime("%Y-%m-%d")
 query=urllib.parse.urlencode({"publicado_desde":day+"T00:00:00","publicado_hasta":day+"T23:59:59",
                              "tamano_pagina":"10","numero_pagina":"1"})
 try:listing=get("https://api2.mercadopublico.cl/v2/compra-agil?"+query)
 except urllib.error.HTTPError as e:
  if e.code==429:
   print("HTTP 429 listado: detener sin reintentos");return
  raise
 items=(listing.get("payload") or {}).get("items") or []
 if not isinstance(items,list):raise SystemExit("Listado API incompatible")
 done=0
 for item in items:
  if done>=limits:break
  code=str(item.get("codigo") or "")
  if not code.endswith("-COT26"):continue
  # No repetir detalles existentes en hoja. Este control evita consultas duplicadas
  # pero seguimiento formal y backfill siguen siendo mejoras independientes.
  if code in existing["Procesos"] and any(k[0]==code for k in existing["Ofertas"]):continue
  done+=1
  time.sleep(3)
  try:data=get("https://api2.mercadopublico.cl/v2/compra-agil/"+urllib.parse.quote(code,safe=""))
  except urllib.error.HTTPError as e:
   print("ERROR_HTTP",e.code,"codigo",code)
   if e.code==429:break
   continue
  p=data.get("payload") or {}
  fechas=p.get("fechas") or {}
  fecha=str(fechas.get("fecha_publicacion") or "")
  if p.get("codigo")!=code or not fecha.startswith(period):
   print("EXCLUIDO_PERIODO",code);continue
  # Contrato MER: solo datos comprobables de detalle oficial; no inventar montos.
  process={"codigo":code,"nombre":str(p.get("nombre") or p.get("titulo") or ""),
           "estado":str(p.get("estado") or ""),
           "convocatoria":str(p.get("convocatoria") or ""),
           "fecha_publicacion":fecha[:10],
           "fecha_cierre":str(fechas.get("fecha_cierre") or "")[:10],
           "organismo_comprador":str(p.get("organismo_comprador") or ""),
           "url_detalle":"https://buscador.mercadopublico.cl/ficha?code="+code,
           "fecha_sincronizacion":now.isoformat(),"categoria":"Compra Ágil",
           "modalidad":"Compra Ágil"}
  converted=adaptar_detalle(data)
  new_p=[process] if code not in existing["Procesos"] else []
  new_o=[r for r in converted["ofertas"] if (r["codigo"],r["id_cotizacion"]) not in existing["Ofertas"]]
  new_r=[r for r in converted["resultados"] if (r["codigo"],r["id_cotizacion_ganadora"]) not in existing["Resultados"]]
  # Hoja de proceso primero, permite relaciones sin huérfanos; lectura previa de claves.
  for name,rows in (("Procesos",new_p),("Ofertas",new_o),("Resultados",new_r)):
   if rows:sheets[name].append_rows([[str(r.get(c,"") or "") for c in SCHEMA[name]] for r in rows],value_input_option="RAW")
  existing["Procesos"].update(r["codigo"] for r in new_p)
  existing["Ofertas"].update((r["codigo"],r["id_cotizacion"]) for r in new_o)
  existing["Resultados"].update((r["codigo"],r["id_cotizacion_ganadora"]) for r in new_r)
  print("OK",code,"Procesos",len(new_p),"Ofertas",len(new_o),"Resultados",len(new_r))
 print("FIN consultas_detalle",done)
if __name__=="__main__":main()
