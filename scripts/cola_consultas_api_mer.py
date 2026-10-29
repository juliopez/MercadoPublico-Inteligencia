#!/usr/bin/env python3
"""Cola complementaria ChileCompra: selección y checkpoint sin red ni escrituras MER.

Entradas: exportación de Procesos (matriz Sheets) y estado privado JSON.
Salida: plan JSON. Exclusivamente Compra Ágil; no consulta la API.
"""
import argparse,datetime as dt,json,pathlib,re
from zoneinfo import ZoneInfo

TZ=ZoneInfo("America/Santiago")
CODE=re.compile(r"^[0-9]+-[0-9]+-COT[0-9]{2}$",re.I)
STATES={"PENDIENTE","ERROR","EN_SEGUIMIENTO","SIN_DATOS","COMPLETO"}
REQUIRED={"codigo","fecha_publicacion","categoria"}
def date(s):
 if not s:return None
 try:return dt.datetime.fromisoformat(str(s).replace("Z","+00:00")).date()
 except ValueError:
  try:return dt.date.fromisoformat(str(s)[:10])
  except ValueError:return None
def process_rows(matrix):
 if not matrix or not isinstance(matrix[0],list):raise ValueError("Falta cabecera Procesos")
 header=matrix[0]
 if len(header)!=len(set(header)) or not REQUIRED.issubset(header):raise ValueError("Esquema Procesos incompatible")
 for raw in matrix[1:]:
  r=dict(zip(header,raw))
  code=str(r.get("codigo","")).strip()
  if CODE.fullmatch(code) and ("COMPRA" in str(r.get("categoria","")).upper() and "ÁGIL" in str(r.get("categoria","")).upper() or "-COT" in code):
   yield code,r
def build(processes,states,day,budget=120,new_cap=None,retry_cap=None,follow_cap=None,etlp_ok=True):
 if not isinstance(states,dict):raise ValueError("Estado inválido")
 if budget<0:raise ValueError("Presupuesto inválido")
 eligible={"nuevos":[],"fallidos":[],"seguimiento":[]}
 seen=set()
 for code,r in process_rows(processes):
  if code in seen:continue
  seen.add(code)
  st=states.get(code)
  if st is None:
   if etlp_ok and date(r.get("fecha_publicacion"))==day:
    eligible["nuevos"].append(code)
   continue
  if st.get("estado") not in STATES:raise ValueError("Estado desconocido: "+code)
  status=st["estado"]
  if status=="ERROR" and date(st.get("proximo_intento")) and date(st["proximo_intento"])<=day:
   eligible["fallidos"].append(code)
  elif status in ("EN_SEGUIMIENTO","SIN_DATOS") and date(st.get("proxima_revision")) and date(st["proxima_revision"])<=day:
   eligible["seguimiento"].append(code)
 # Reservas equilibradas configurables para evitar que los nuevos absorban toda la cuota.
 caps=[new_cap,retry_cap,follow_cap]
 if any(x is not None and x<0 for x in caps):raise ValueError("Cupo negativo")
 if all(x is None for x in caps):
  new_cap=(budget+1)//2
  retry_cap=max(1,budget//4) if budget else 0
  follow_cap=budget-new_cap-retry_cap
 caps={"nuevos":new_cap,"fallidos":retry_cap,"seguimiento":follow_cap}
 selected=[];used=set()
 for group in ("nuevos","fallidos","seguimiento"):
  for code in sorted(eligible[group])[:caps[group] if caps[group] is not None else budget]:
   if code not in used and len(selected)<budget:
    selected.append({"codigo":code,"grupo":group})
    used.add(code)
 # Redistribuir cupos sin dejar recursos ociosos.
 for group in ("nuevos","fallidos","seguimiento"):
  for code in sorted(eligible[group]):
   if len(selected)>=budget:break
   if code not in used:
    selected.append({"codigo":code,"grupo":group});used.add(code)
 return {"fecha":day.isoformat(),"presupuesto":budget,"consultas":selected,
         "candidatos":{g:len(v) for g,v in eligible.items()},
         "sin_consulta":sum(map(len,eligible.values()))-len(selected)}
def checkpoint(states,code,result,day,sha="",error=""):
 if result not in ("ok_pendiente","ok_sin_datos","ok_completo","error"):
  raise ValueError("Resultado inválido")
 d=dict(states);old=dict(d.get(code,{}))
 tries=int(old.get("intentos",0))+(1 if result=="error" else 0)
 new=dict(old,codigo=code,ultimo_intento=day.isoformat(),intentos=tries)
 if result=="error":
  delay=[1,2,4,7][min(tries-1,3)]
  new.update(estado="ERROR",tipo_error=error[:100],proximo_intento=(day+dt.timedelta(days=delay)).isoformat())
 else:
  new.update(ultima_consulta_exitosa=day.isoformat(),hash_respuesta=sha,tipo_error="",proximo_intento="")
  if result=="ok_completo":new.update(estado="COMPLETO",proxima_revision="")
  elif result=="ok_sin_datos":new.update(estado="SIN_DATOS",proxima_revision=(day+dt.timedelta(days=7)).isoformat())
  else:
   first=date(old.get("primera_consulta_exitosa")) or day
   age=(day-first).days
   new.update(estado="EN_SEGUIMIENTO",primera_consulta_exitosa=first.isoformat(),
              proxima_revision=(day+dt.timedelta(days=2 if age<14 else 7)).isoformat())
 d[code]=new
 return d
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--procesos-json",required=True)
 p.add_argument("--estado-json",required=True)
 p.add_argument("--fecha",default=dt.datetime.now(TZ).date().isoformat())
 p.add_argument("--presupuesto",type=int,default=120)
 p.add_argument("--etl-fallido",action="store_true")
 p.add_argument("--salida",required=True)
 a=p.parse_args()
 pro=json.loads(pathlib.Path(a.procesos_json).read_text())
 statefile=pathlib.Path(a.estado_json)
 state=json.loads(statefile.read_text()) if statefile.exists() else {}
 report=build(pro,state,dt.date.fromisoformat(a.fecha),a.presupuesto,etlp_ok=not a.etl_fallido)
 pathlib.Path(a.salida).write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps({"candidatos":report["candidatos"],"planificados":len(report["consultas"])}))
if __name__=="__main__":main()
