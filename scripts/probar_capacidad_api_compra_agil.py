#!/usr/bin/env python3
"""Prueba de capacidad API Compra Ágil: solo HTTP GET; nunca escribe en MER/Git."""
import argparse,datetime as dt,json,os,pathlib,sys,time,urllib.error,urllib.parse,urllib.request
from zoneinfo import ZoneInfo

TZ=ZoneInfo("America/Santiago")
def fetch(url,ticket):
 req=urllib.request.Request(url,headers={"ticket":ticket,"Accept":"application/json","User-Agent":"Observatorio-MER-Capacidad/1"})
 with urllib.request.urlopen(req,timeout=35) as resp:
  raw=resp.read(2000001)
  if len(raw)>2000000:raise ValueError("Respuesta API mayor que 2 MB")
  return json.loads(raw)
def main():
 ap=argparse.ArgumentParser(description="Prueba real sin escritura de datos")
 ap.add_argument("--periodo",default="2026-10",help="Mes de publicación a consultar, AAAA-MM")
 ap.add_argument("--limite",type=int,choices=(10,25,50),default=25)
 ap.add_argument("--pausa",type=float,default=3)
 args=ap.parse_args()
 if args.pausa<3:ap.error("Pausa mínima 3 segundos")
 if len(args.periodo)!=7 or args.periodo[4]!="-":ap.error("Período inválido")
 ticket=os.getenv("CHILECOMPRA_TICKET","").strip()
 if not ticket:raise SystemExit("Falta CHILECOMPRA_TICKET en entorno privado")
 begin=time.monotonic()
 codes=[];seen=set();pages=0;calls=0;errors=[];details=0
 date=dt.date.fromisoformat(args.periodo+"-01")
 last=(date.replace(day=28)+dt.timedelta(days=4)).replace(day=1)-dt.timedelta(days=1)
 print("PRUEBA_API_SOLO_LECTURA",args.periodo,"limite",args.limite,flush=True)
 try:
  while date<=last and len(codes)<args.limite:
   page=1
   while len(codes)<args.limite:
    q=urllib.parse.urlencode({"publicado_desde":date.isoformat()+"T00:00:00","publicado_hasta":date.isoformat()+"T23:59:59","tamano_pagina":"10","numero_pagina":str(page),"ordenar_por":"FechaPublicacion"})
    try:
     t=time.monotonic()
     resp=fetch("https://api2.mercadopublico.cl/v2/compra-agil?"+q,ticket)
     calls+=1;pages+=1
     payload=resp.get("payload") or {}
     if resp.get("success") not in (True,"OK") or not isinstance(payload.get("items"),list):raise ValueError("Listado incompatible")
     items=payload["items"]
     for item in items:
      c=str(item.get("codigo") or "") if isinstance(item,dict) else ""
      if c.endswith("-COT26") and c not in seen and len(codes)<args.limite:codes.append(c);seen.add(c)
     total_pages=int((payload.get("paginacion") or {}).get("total_paginas") or page)
     print("LISTADO",date,"pagina",page,"codigos",len(codes),"segundos",round(time.monotonic()-t,2),flush=True)
     if page>=total_pages:break
     page+=1
     time.sleep(args.pausa)
    except urllib.error.HTTPError as e:
     calls+=1;errors.append("listado: HTTP "+str(e.code));raise
   date+=dt.timedelta(days=1)
  for code in codes:
   time.sleep(args.pausa)
   try:
    t=time.monotonic();r=fetch("https://api2.mercadopublico.cl/v2/compra-agil/"+urllib.parse.quote(code,safe=""),ticket)
    calls+=1
    p=r.get("payload") or {}
    if not isinstance(p,dict) or p.get("codigo")!=code:raise ValueError("Detalle incompatible "+code)
    details+=1
    print("DETALLE",details,"de",len(codes),"segundos",round(time.monotonic()-t,2),flush=True)
   except urllib.error.HTTPError as e:
    calls+=1;errors.append("detalle: HTTP "+str(e.code));print("DETENIDO_HTTP",e.code,flush=True);break
   except Exception as e:
    errors.append(type(e).__name__);print("ERROR_DETALLE",type(e).__name__,flush=True);break
 except urllib.error.HTTPError as e:print("DETENIDO_HTTP_LISTADO",e.code,flush=True)
 finally:
  summary={"modo":"SOLO_LECTURA_SIN_SHEETS_NI_GIT","periodo":args.periodo,"limite":args.limite,"paginas":pages,"codigos_encontrados":len(codes),"detalles_correctos":details,"llamadas_http":calls,"errores":errors,"duracion_segundos":round(time.monotonic()-begin,1)}
  print("RESUMEN_PRUEBA_API",json.dumps(summary,ensure_ascii=False),flush=True)
  if details<args.limite or errors:sys.exit(2)
if __name__=="__main__":main()
