#!/usr/bin/env python3
"""Auditoría campo a campo MER v2: origen SQLite vs instantánea local de Sheets.
No abre conexiones, no aplica escrituras ni decide precedencia automáticamente.
Formato instantánea: SQLite con seis tablas(pk TEXT PRIMARY KEY,fila TEXT).
"""
import argparse,collections,datetime as dt,importlib.util,json,sqlite3
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
def schemas():
 spec=importlib.util.spec_from_file_location("mer",ROOT/"scripts/importador_historicos_v2.py")
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 return mod.SCHEMA
def diferencias(oficial,operativo,esquemas,muestra=3):
 res={}
 for table,cols in esquemas.items():
  conteos=collections.Counter();sample={}
  old={pk:json.loads(raw) for pk,raw in operativo.execute('SELECT pk,fila FROM "'+table+'"')}
  for pk,raw in oficial.execute('SELECT pk,fila FROM "'+table+'"'):
   nuevo=json.loads(raw)
   if len(nuevo)!=len(cols) or nuevo[0]!=pk:raise ValueError("Origen inválido "+table)
   anterior=old.pop(pk,None)
   if anterior is None:
    conteos["solo_oficial"]+=1
    continue
   if len(anterior)!=len(cols) or anterior[0]!=pk:raise ValueError("Operativo inválido "+table)
   fields=[name for name,a,b in zip(cols,anterior,nuevo) if str(a or "")!=str(b or "")]
   if not fields:conteos["iguales"]+=1;continue
   conteos["modificados"]+=1
   for name in fields:
    conteos["campo:"+name]+=1
    if len(sample.setdefault(name,[]))<muestra:sample[name].append(pk)
  conteos["solo_operativo"]=len(old)
  res[table]={"iguales":conteos["iguales"],"nuevos":conteos["solo_oficial"],
              "modificados":conteos["modificados"],"solo_operativo":conteos["solo_operativo"],
              "campos_modificados":{k[6:]:v for k,v in conteos.items() if k.startswith("campo:")},
              "muestras_pk_por_campo":sample}
 return res
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--oficial",type=Path,required=True)
 p.add_argument("--operativo-snapshot",type=Path,required=True)
 p.add_argument("--salida",type=Path,required=True)
 a=p.parse_args()
 with sqlite3.connect(f"file:{a.oficial.resolve()}?mode=ro",uri=True) as src,sqlite3.connect(f"file:{a.operativo_snapshot.resolve()}?mode=ro",uri=True) as dst:
  summary=diferencias(src,dst,schemas())
 output={"fecha_chile":dt.datetime.now(ZoneInfo("America/Santiago")).isoformat(),
         "estado":"DIFERENCIAS_POR_CAMPO_REQUIEREN_DECISION",
         "tablas":summary,"aplicar_autorizado":False,"cierre_autorizado":False,
         "nota":"No sobrescribir estados, adjudicaciones ni campos validados sin regla aprobada y evidencia"}
 a.salida.parent.mkdir(parents=True,exist_ok=True)
 a.salida.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print("AUDITORIA CAMPO A CAMPO:",a.salida)
if __name__=="__main__":main()
