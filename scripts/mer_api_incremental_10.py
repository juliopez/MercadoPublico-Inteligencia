#!/usr/bin/env python3
"""Compra Ágil MER: hasta 10 detalles/día, estado persistido en Git, sin Ubuntu."""
import datetime as dt,json,os,pathlib,time,urllib.error,urllib.parse,urllib.request
from zoneinfo import ZoneInfo
from adaptar_detalle_compra_agil_mer import adaptar_detalle
from importador_historicos_v2 import SCHEMA
from normalizar_procesos_api_mer import proceso as normalizar_proceso, completar_proceso

ROOT=pathlib.Path(__file__).resolve().parents[1]
STATE=ROOT/"control"/"cola_api_mer.json"
TZ=ZoneInfo("America/Santiago")
def fetch(url,ticket):
 req=urllib.request.Request(url,headers={"ticket":ticket,"Accept":"application/json","User-Agent":"Observatorio-MER-GHA/2"})
 with urllib.request.urlopen(req,timeout=35) as resp:
  raw=resp.read(2000001)
  if len(raw)>2000000:raise ValueError("respuesta demasiado extensa")
  return json.loads(raw)

def period_ok(obj,code,period):
 p=obj.get("payload")
 if not isinstance(p,dict) or p.get("codigo")!=code:raise ValueError("codigo respuesta incompatible")
 date=str((p.get("fechas") or {}).get("fecha_publicacion") or "")
 if not date.startswith(period):raise ValueError("fecha publicación fuera del mes")
 return p,date

def main():
 import gspread
 from google.oauth2.service_account import Credentials
 now=dt.datetime.now(TZ)
 if os.getenv("MER_API_RUN_NOW")!="1" and (now.weekday()>4 or now.hour!=22):
  print("SKIP: fuera de las 22 horas America/Santiago");return
 ticket=os.getenv("CHILECOMPRA_TICKET","").strip()
 secret=os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON","").strip()
 if not ticket or not secret:raise SystemExit("BLOQUEO: falta secreto de API o de escritura Google Sheets")
 maximum=int(os.getenv("MER_API_MAX_DETAIL","10"))
 if maximum!=10:raise SystemExit("BLOQUEO: se requieren exactamente 10 como máximo")
 period=now.strftime("%Y-%m")
 cat=json.loads((ROOT/"config/catalogo_sheets.json").read_text())
 dest=cat["periodos"].get(period)
 if not dest or dest.get("tipo")!="operativo":raise SystemExit("BLOQUEO: mes operativo inexistente")
 creds=Credentials.from_service_account_info(json.loads(secret),scopes=["https://www.googleapis.com/auth/spreadsheets"])
 book=gspread.authorize(creds).open_by_key(dest["id"])
 names=("Procesos","Ofertas","Resultados")
 sheets={k:book.worksheet(k) for k in names}
 existing={k:sheets[k].get_all_values() for k in names}
 for k in names:
  if not existing[k] or existing[k][0]!=SCHEMA[k]:raise ValueError("Esquema incompatible "+k)
 keys={
  "Procesos":{r[0] for r in existing["Procesos"][1:] if r},
  "Ofertas":{(r[1],r[0]) for r in existing["Ofertas"][1:] if len(r)>1},
  "Resultados":{(r[0],r[1]) for r in existing["Resultados"][1:] if len(r)>1},
 }
 STATE.parent.mkdir(parents=True,exist_ok=True)
 state=json.loads(STATE.read_text()) if STATE.exists() else {"periodos":{}}
 window=state.setdefault("periodos",{}).setdefault(period,{"pagina":1,"consultas":{}})
 cache=window["consultas"]
 today=now.date().isoformat()
 # Primero reintentos vencidos y seguimientos vencidos; después nuevos por fecha ascendente.
 follow=sorted([c for c,e in cache.items() if e.get("estado") in ("ERROR","EN_SEGUIMIENTO","SIN_DATOS") and e.get("proxima_revision","9999")<=today],key=lambda c:(cache[c].get("proxima_revision",""),c))
 candidates=follow[:2]
 test_code=os.getenv("MER_API_TEST_CODE","").strip()
 if test_code:
  if test_code not in cache or test_code not in keys["Procesos"]:raise SystemExit("BLOQUEO: el código de prueba debe existir en cola y MER")
  candidates=[test_code]
 page=int(window.get("pagina",1))
 date_cursor=window.get("fecha_cursor",period+"-01")
 if date_cursor>today:
  print("Sin nuevas fechas publicadas pendientes; revisar seguimientos")
 total_pages=None
 if len(candidates)<maximum and not test_code:
  query=urllib.parse.urlencode({"publicado_desde":date_cursor+"T00:00:00","publicado_hasta":date_cursor+"T23:59:59",
          "tamano_pagina":"10","numero_pagina":str(page),"ordenar_por":"FechaPublicacion"})
  try:listed=fetch("https://api2.mercadopublico.cl/v2/compra-agil?"+query,ticket)
  except urllib.error.HTTPError as e:
   if e.code==429:
    print("STOP HTTP 429 listado sin escrituras");return
   raise
  payload=listed.get("payload") or {}
  if listed.get("success") not in (True,"OK") or not isinstance(payload.get("items"),list):raise ValueError("Listado API incompatible")
  total_pages=int((payload.get("paginacion") or {}).get("total_paginas") or page)
  items=payload["items"]
  listing_codes=[str(i.get("codigo") or "") for i in items if isinstance(i,dict)]
  for code in listing_codes:
   if code.endswith("-COT26") and code not in cache and code not in candidates and len(candidates)<maximum:candidates.append(code)
  # Avance solo si los registros de esta página están en cache o fueron seleccionados.
  can_advance=all(not c.endswith("-COT26") or c in cache or c in candidates for c in listing_codes)
 else:
  can_advance=False
 report={"periodo":period,"fecha":today,"consultados":0,"procesos":0,"ofertas":0,"resultados":0,"errores":0,"pagina":page}
 try:
  for code in candidates:
   time.sleep(3)
   try:
    raw=fetch("https://api2.mercadopublico.cl/v2/compra-agil/"+urllib.parse.quote(code,safe=""),ticket)
    p,pub=period_ok(raw,code,period)
    result=adaptar_detalle(raw)
    # Aplanar campos oficiales; no escribir objetos en celdas.
    process=normalizar_proceso(p,code,pub,now)
    if code in keys["Procesos"]:
     for i,old_row in enumerate(existing["Procesos"][1:],2):
      if old_row and old_row[0]==code:
       old=dict(zip(SCHEMA["Procesos"],old_row+[""]*len(SCHEMA["Procesos"])))
       merged=completar_proceso(old,process)
       if merged!=old:
        sheets["Procesos"].update(range_name=f"A{i}:P{i}",values=[[str(merged.get(k,"") or "") for k in SCHEMA["Procesos"]]],value_input_option="RAW")
        existing["Procesos"][i-1]=[str(merged.get(k,"") or "") for k in SCHEMA["Procesos"]]
        report["procesos_enriquecidos"]=report.get("procesos_enriquecidos",0)+1
       break
    proposed={
      "Procesos":[process] if code not in keys["Procesos"] else [],
      "Ofertas":[r for r in result["ofertas"] if (r["codigo"],r["id_cotizacion"]) not in keys["Ofertas"]],
      "Resultados":[r for r in result["resultados"] if (r["codigo"],r["id_cotizacion_ganadora"]) not in keys["Resultados"]]
    }
    # Completar únicamente celdas vacías en ofertas y resultados anteriores.
    # Proteger identidades, selección y validaciones ya establecidas.
    for name,newrows,key_fields in (("Ofertas",result["ofertas"],("codigo","id_cotizacion")),
                                    ("Resultados",result["resultados"],("codigo","id_cotizacion_ganadora"))):
     columns=SCHEMA[name]
     oldindex={}
     for row_number,rawrow in enumerate(existing[name][1:],2):
      if not rawrow:continue
      previous=dict(zip(columns,rawrow+[""]*len(columns)))
      oldindex[tuple(previous.get(k,"") for k in key_fields)]=(row_number,previous)
     for fresh in newrows:
      k=tuple(str(fresh.get(field,"") or "") for field in key_fields)
      if k not in oldindex:continue
      row_number,previous=oldindex[k]
      merged=dict(previous)
      for field in columns:
       if field in ("seleccionado","validado","id_proveedor","id_cotizacion","codigo","id_cotizacion_ganadora"):continue
       new_value=str(fresh.get(field,"") or "")
       if not merged.get(field) and new_value:merged[field]=new_value
      if merged!=previous:
       sheets[name].update(range_name=f"A{row_number}:{'I' if name=='Ofertas' else 'J'}{row_number}",values=[[str(merged.get(field,"") or "") for field in columns]],value_input_option="RAW")
       existing[name][row_number-1]=[str(merged.get(field,"") or "") for field in columns]
       report[name.lower()+"_enriquecidos"]=report.get(name.lower()+"_enriquecidos",0)+1
    # Se revalidan claves justo antes de insertar: no sobrescribir valores previos.
    for name in names:
     if proposed[name]:
      sheets[name].append_rows([[str(r.get(f,"") or "") for f in SCHEMA[name]] for r in proposed[name]],value_input_option="RAW")
      if name=="Procesos":keys[name].update(r["codigo"] for r in proposed[name])
      if name=="Ofertas":keys[name].update((r["codigo"],r["id_cotizacion"]) for r in proposed[name])
      if name=="Resultados":keys[name].update((r["codigo"],r["id_cotizacion_ganadora"]) for r in proposed[name])
      report[name.lower()]+=len(proposed[name])
    # Relectura posterior de claves confirma la escritura.
    for name in names:
     if proposed[name]:
      rows=sheets[name].get_all_values()[1:]
      real={r[0] for r in rows if r} if name=="Procesos" else {(r[1],r[0]) for r in rows if len(r)>1} if name=="Ofertas" else {(r[0],r[1]) for r in rows if len(r)>1}
      for r in proposed[name]:
       k=r["codigo"] if name=="Procesos" else (r["codigo"],r["id_cotizacion"] if name=="Ofertas" else r["id_cotizacion_ganadora"])
       if k not in real:raise RuntimeError("Verificación de escritura fallida "+name)
    # Selección API no acredita resultado jurídico definitivo.
    status="EN_SEGUIMIENTO"
    cache[code]={"estado":status,"ultima_consulta":today,"proxima_revision":(now.date()+dt.timedelta(days=3)).isoformat(), "intentos":0}
    report["consultados"]+=1
   except urllib.error.HTTPError as exc:
    wait=2 if exc.code==429 else 1
    cache[code]={"estado":"ERROR","ultima_consulta":today,"proxima_revision":(now.date()+dt.timedelta(days=wait)).isoformat(),"intentos":int(cache.get(code,{}).get("intentos",0))+1,"error":"HTTP "+str(exc.code)}
    report["errores"]+=1
    if exc.code==429:break
   except Exception as exc:
    cache[code]={"estado":"ERROR","ultima_consulta":today,"proxima_revision":(now.date()+dt.timedelta(days=2)).isoformat(),"intentos":int(cache.get(code,{}).get("intentos",0))+1,"error":type(exc).__name__}
    report["errores"]+=1
 finally:
  if not test_code and can_advance and total_pages:
   if page<total_pages:window["pagina"]=page+1
   else:
    window["pagina"]=1
    window["fecha_cursor"]=(dt.date.fromisoformat(date_cursor)+dt.timedelta(days=1)).isoformat()
  STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n")
  pathlib.Path(os.environ.get("GITHUB_STEP_SUMMARY","/tmp/mer_summary")).write_text("MER API: "+json.dumps(report,ensure_ascii=False)+"\n")
  pathlib.Path("control/ultimo_reporte_api_mer.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
  print(json.dumps(report,ensure_ascii=False))
if __name__=="__main__":main()
