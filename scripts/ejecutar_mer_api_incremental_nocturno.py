#!/usr/bin/env python3
"""MER Compra Ágil: micro-lotes nocturnos, fail-closed ante 429 o credenciales ausentes."""
import datetime as dt,json,os,pathlib,time,urllib.request,urllib.error,urllib.parse
from zoneinfo import ZoneInfo
from adaptar_detalle_compra_agil_mer import adaptar_detalle,OFERTAS,RESULTADOS
TZ=ZoneInfo("America/Santiago")
COLS=["codigo","estado","ultimo_intento","proximo_intento","intentos","ultima_consulta_exitosa","detalle"]
def main():
 import gspread
 from google.oauth2.service_account import Credentials
 now=dt.datetime.now(TZ)
 if now.hour!=22:raise SystemExit("BLOQUEO: no es ventana 22h Santiago")
 ticket=os.environ.get("CHILECOMPRA_TICKET","").strip()
 cred=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS","")
 if not ticket or not cred or not pathlib.Path(cred).is_file():raise SystemExit("BLOQUEO: faltan credenciales")
 limit=int(os.environ.get("MER_API_MAX_DETAIL","5"))
 if not 1<=limit<=10:raise SystemExit("BLOQUEO: máximo permitido 10 detalles por ejecución")
 cat=json.loads((pathlib.Path(__file__).resolve().parents[1]/"config/catalogo_sheets.json").read_text())
 period=now.strftime("%Y-%m")
 target=cat["periodos"].get(period)
 if not target or target["tipo"]!="operativo":raise SystemExit("BLOQUEO: mes operativo no identificado")
 service=Credentials.from_service_account_file(cred,scopes=["https://www.googleapis.com/auth/spreadsheets"])
 book=gspread.authorize(service).open_by_key(target["id"])
 offer_ws=book.worksheet("Ofertas");result_ws=book.worksheet("Resultados")
 try:control=book.worksheet("_Control_API")
 except gspread.WorksheetNotFound:
  # No crear una nueva pestaña automáticamente en un libro oficial validado.
  raise SystemExit("BLOQUEO: requiere pestaña privada _Control_API aprobada y preparada")
 if control.row_values(1)!=COLS:raise SystemExit("BLOQUEO: cabecera del control incorrecta")
 stored=control.get_all_records()
 known={str(r["codigo"]):r for r in stored if r.get("codigo")}
 def http(url):
  req=urllib.request.Request(url,headers={"ticket":ticket,"Accept":"application/json","User-Agent":"MER-incremental/1"})
  with urllib.request.urlopen(req,timeout=35) as resp:return json.load(resp)
 def update(code,state,nextdate,attempts,detail):
  row=next((i for i,r in enumerate(stored,2) if str(r.get("codigo"))==code),None)
  values=[code,state,now.date().isoformat(),nextdate,attempts,now.isoformat() if state!="ERROR" else "",detail[:150]]
  if row:control.update(range_name=f"A{row}:G{row}",values=[values],value_input_option="RAW")
  else:
   control.append_row(values,value_input_option="RAW")
   stored.append(dict(zip(COLS,values)))
 def eligible(code):
  s=known.get(code)
  return not s or s["estado"]!="COMPLETO" and (not s.get("proximo_intento") or str(s["proximo_intento"])<=now.date().isoformat())
 # Una página pequeña por ejecución; cursor implícito basado en día (rotación configurable)
 page=int(os.environ.get("MER_API_PAGE","1"))
 if not 1<=page<=100000:raise SystemExit("BLOQUEO: página fuera de rango")
 # Nunca asumir que la OC identifica el mes de publicación.
 query={"publicado_desde":f"{period}-01T00:00:00","publicado_hasta":now.strftime("%Y-%m-%dT23:59:59"),
        "tamano_pagina":"10","numero_pagina":str(page),"ordenar_por":"FechaPublicacion"}
 try:listing=http("https://api2.mercadopublico.cl/v2/compra-agil?"+urllib.parse.urlencode(query))
 except urllib.error.HTTPError as e:
  if e.code==429:raise SystemExit("HTTP 429: sin más consultas; reintentar en próxima ventana") from None
  raise
 payload=listing.get("payload") or {}
 rows=payload.get("resultados") or payload.get("items") or payload.get("datos") or []
 if not isinstance(rows,list):raise SystemExit("BLOQUEO: esquema de listado inesperado")
 existing_off=offer_ws.get_all_values()
 existing_res=result_ws.get_all_values()
 if existing_off[0]!=list(OFERTAS) or existing_res[0]!=list(RESULTADOS):raise SystemExit("BLOQUEO: contrato MER alterado")
 keys={(r[1],r[0]) for r in existing_off[1:] if len(r)>=2}
 resultkeys={(r[0],r[1]) for r in existing_res[1:] if len(r)>=2}
 count=0
 for item in rows:
  code=str(item.get("codigo") or "").strip()
  if not code.endswith("-COT26") or not eligible(code):continue
  if count>=limit:break
  count+=1
  try:
   data=http("https://api2.mercadopublico.cl/v2/compra-agil/"+urllib.parse.quote(code,safe=""))
   p=data.get("payload") or {}
   publication=str((p.get("fechas") or {}).get("fecha_publicacion") or "")
   if not publication.startswith(period):raise ValueError("Proceso no pertenece al mes operativo")
   adapted=adaptar_detalle(data)
   offers=adapted["ofertas"];results=adapted["resultados"]
   new=[r for r in offers if (r["codigo"],r["id_cotizacion"]) not in keys]
   newres=[r for r in results if (r["codigo"],r["id_cotizacion_ganadora"]) not in resultkeys]
   if new:offer_ws.append_rows([[r.get(c,"") for c in OFERTAS] for r in new],value_input_option="RAW")
   if newres:result_ws.append_rows([[r.get(c,"") for c in RESULTADOS] for r in newres],value_input_option="RAW")
   keys.update((r["codigo"],r["id_cotizacion"]) for r in new)
   resultkeys.update((r["codigo"],r["id_cotizacion_ganadora"]) for r in newres)
   # No declarar completo si selección o adjudicación futura puede cambiar.
   update(code,"EN_SEGUIMIENTO",(now.date()+dt.timedelta(days=3)).isoformat(),0,f"ofertas_nuevas={len(new)};resultados_nuevos={len(newres)}")
  except urllib.error.HTTPError as e:
   if e.code==429:
    update(code,"ERROR",(now.date()+dt.timedelta(days=2)).isoformat(),int(known.get(code,{}).get("intentos") or 0)+1,"HTTP 429")
    break
   update(code,"ERROR",(now.date()+dt.timedelta(days=2)).isoformat(),int(known.get(code,{}).get("intentos") or 0)+1,f"HTTP {e.code}")
  except Exception as e:
   update(code,"ERROR",(now.date()+dt.timedelta(days=2)).isoformat(),int(known.get(code,{}).get("intentos") or 0)+1,type(e).__name__)
  time.sleep(2)
 print(json.dumps({"periodo":period,"detalles_intentados":count,"limite":limit,"pagina":page}))
if __name__=="__main__":main()
