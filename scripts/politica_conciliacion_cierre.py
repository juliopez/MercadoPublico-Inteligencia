#!/usr/bin/env python3
"""Política conservadora MER v2 para conciliar columnas del mismo PK.

No conecta con Sheets ni ejecuta escritura. Reglas:
- Misma clave / valores iguales: conservar.
- Origen oficial aporta dato donde operativo está vacío: completar.
- Operativo contiene dato y oficial vacío: conservar operativo.
- Dos valores distintos y no vacíos: conflicto que exige revisión.
- La identidad (primera columna PK) nunca puede cambiar.
Las reglas rigen las seis entidades; no atribuyen validez jurídica.
"""
import argparse,collections,datetime as dt,importlib.util,json,sqlite3
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
def esquema():
 spec=importlib.util.spec_from_file_location("mer_hist",ROOT/"scripts/importador_historicos_v2.py")
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod.SCHEMA
def conciliar_fila(cols,operativa,oficial):
 if len(operativa)!=len(cols) or len(oficial)!=len(cols):raise ValueError("Filas con contrato incompatible")
 if not operativa[0] or operativa[0]!=oficial[0]:raise ValueError("PK divergente")
 merged=list(operativa);changes=[];conflicts=[]
 for i in range(1,len(cols)):
  old=str(operativa[i] or "").strip();new=str(oficial[i] or "").strip()
  if old==new:continue
  if not old and new:
   merged[i]=oficial[i];changes.append(cols[i])
  elif old and new:
   conflicts.append(cols[i])
 return merged,changes,conflicts

def auditar(origen,destino,schemas,sample=5):
 summary={}; conflict_count=0
 for t,cols in schemas.items():
  operative={pk:json.loads(raw) for pk,raw in destino.execute('SELECT pk,fila FROM "'+t+'"')}
  counts=collections.Counter(); conflicts=collections.Counter();ex={}
  for pk,raw in origen.execute('SELECT pk,fila FROM "'+t+'"'):
   official=json.loads(raw)
   if len(official)!=len(cols) or official[0]!=pk:raise ValueError("Origen inválido "+t)
   previous=operative.pop(pk,None)
   if previous is None:counts["nuevos"]+=1;continue
   _,enriched,issues=conciliar_fila(cols,previous,official)
   if enriched:counts["enriquecidos"]+=1
   if issues:
    counts["conflictivos"]+=1
    for field in issues:
     conflicts[field]+=1
     if len(ex.setdefault(field,[]))<sample:ex[field].append(pk)
   elif not enriched:counts["iguales_o_preservados"]+=1
  counts["solo_operativos"]=len(operative)
  summary[t]={"conteos":dict(counts),"conflictos_por_campo":dict(conflicts),"ejemplos_pk":ex}
  conflict_count+=counts["conflictivos"]
 return {"estado":"BLOQUEADO_CONFLICTOS" if conflict_count else "PROPUESTA_SIN_CONFLICTOS_PENDIENTE_AUDITORIA",
         "conflictos_totales":conflict_count,"tablas":summary,
         "escritura_autorizada":False,"traslado_autorizado":False}

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--oficial",required=True,type=Path)
 p.add_argument("--operativo-snapshot",required=True,type=Path)
 p.add_argument("--salida",required=True,type=Path)
 a=p.parse_args()
 with sqlite3.connect(f"file:{a.oficial.resolve()}?mode=ro",uri=True) as src,sqlite3.connect(f"file:{a.operativo_snapshot.resolve()}?mode=ro",uri=True) as dst:
  result=auditar(src,dst,esquema())
 result["fecha_chile"]=dt.datetime.now(ZoneInfo("America/Santiago")).isoformat()
 a.salida.parent.mkdir(parents=True,exist_ok=True)
 a.salida.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("POLÍTICA MER:",result["estado"],"conflictos",result["conflictos_totales"])
if __name__=="__main__":main()
