#!/usr/bin/env python3
"""Auditoría referencial MER v2 del paquete SQLite, sin escrituras ni red.

Errores: PK/fila incoherente, esquema roto, referencias a ofertas existentes
que apuntan a otro proceso, resultados marcados jurídicamente validados por un
histórico sin evidencia. Observaciones: FK ausentes por cortes entre meses.
"""
import argparse,collections,datetime as dt,importlib.util,json,sqlite3
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
TABLES=("Procesos","Ofertas","Resultados","OrdenesCompra","Proveedores","VinculosCOT_OC")
def schema():
 spec=importlib.util.spec_from_file_location("mer",ROOT/"scripts/importador_historicos_v2.py")
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m.SCHEMA
def auditar(db,schemas):
 errors=collections.Counter();notes=collections.Counter();counts={}
 keys={}
 for t in TABLES:
  rows={}
  for pk,raw in db.execute('SELECT pk,fila FROM "'+t+'"'):
   row=json.loads(raw)
   if len(row)!=len(schemas[t]) or not row or row[0]!=pk:errors[t+"_contrato_o_pk"]+=1;continue
   rows[pk]=row
  keys[t]=rows;counts[t]=len(rows)
 for row in keys["Ofertas"].values():
  if row[1] not in keys["Procesos"]:notes["ofertas_proceso_fuera_de_corte"]+=1
  if row[2] and row[2] not in keys["Proveedores"]:notes["ofertas_proveedor_no_resuelto"]+=1
 for row in keys["Resultados"].values():
  if row[0] not in keys["Procesos"]:notes["resultados_proceso_fuera_de_corte"]+=1
  if row[1]:
   offer=keys["Ofertas"].get(row[1])
   if not offer:notes["resultado_oferta_no_disponible"]+=1
   elif offer[1]!=row[0]:errors["resultado_oferta_de_otro_proceso"]+=1
  if str(row[7]).strip().lower() in ("true","si","sí","1","validado"):
   errors["resultado_historico_marcado_validado"]+=1
 for row in keys["OrdenesCompra"].values():
  if row[1] and row[1] not in keys["Procesos"]:notes["oc_proceso_fuera_de_corte"]+=1
  if row[2] and row[2] not in keys["Proveedores"]:notes["oc_proveedor_no_resuelto"]+=1
 for row in keys["VinculosCOT_OC"].values():
  if not row[2] or row[2].upper() in ("NA","NULL","NONE"):errors["vinculo_sin_oc"]+=1
  if row[1] not in keys["Procesos"]:notes["vinculo_proceso_fuera_de_corte"]+=1
  if row[2] not in keys["OrdenesCompra"]:notes["vinculo_oc_fuera_de_corte"]+=1
  if row[2] in keys["OrdenesCompra"] and row[1] and keys["OrdenesCompra"][row[2]][1] and row[1]!=keys["OrdenesCompra"][row[2]][1]:
   notes["vinculo_proceso_oc_diferente"]+=1
 return {"estado":"AUDITORIA_BLOQUEADA" if errors else "AUDITORIA_ESTRUCTURAL_SIN_ERRORES_CON_OBSERVACIONES",
         "conteos":counts,"errores_bloqueantes":dict(errors),"observaciones":dict(notes),
         "cierre_autorizado":False,"traslado_autorizado":False}
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--paquete",type=Path,required=True)
 p.add_argument("--salida",type=Path)
 a=p.parse_args()
 report=json.loads((a.paquete/"informe.json").read_text(encoding="utf-8"))
 if report.get("validacion_filas")!="OK":p.error("Paquete no validado")
 db=sqlite3.connect(f"file:{(a.paquete/'preparado.sqlite').resolve()}?mode=ro",uri=True)
 try:result=auditar(db,schema())
 finally:db.close()
 if any(result["conteos"][t]!=report[t] for t in TABLES):
  raise ValueError("Conteos del informe no coinciden con SQLite")
 result.update({"periodo":report["periodo"],"fecha_chile":dt.datetime.now(ZoneInfo("America/Santiago")).isoformat(),
                "escrituras_google":False})
 out=a.salida or a.paquete.parent/"auditoria_referencial.json"
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(result,ensure_ascii=False,indent=2))
 if result["errores_bloqueantes"]:raise SystemExit(2)
if __name__=="__main__":main()
