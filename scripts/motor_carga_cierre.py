#!/usr/bin/env python3
"""Motor de carga MER de cierre. SIMULACION por diseño, sin credenciales ni red.

Construye acciones reproducibles y simula reintentos en SQLite LOCAL. La fase
Google Sheets real permanece deshabilitada hasta auditoría y autorización.
"""
import argparse,datetime as dt,json,sqlite3,hashlib
from pathlib import Path
from zoneinfo import ZoneInfo

TABLES=("Procesos","Ofertas","Resultados","OrdenesCompra","Proveedores","VinculosCOT_OC")

def digest(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
 return h.hexdigest()

def plan_local(source,operativo):
 """Devuelve conteos candidatos; conserva solo-operativos y no elimina."""
 result={}
 for table in TABLES:
  lhs={k:json.loads(v) for k,v in source.execute('SELECT pk,fila FROM "'+table+'"')}
  rhs={k:json.loads(v) for k,v in operativo.execute('SELECT pk,fila FROM "'+table+'"')}
  result[table]={"nuevos":sum(k not in rhs for k in lhs),
   "modificados":sum(k in rhs and rhs[k]!=v for k,v in lhs.items()),
   "iguales":sum(k in rhs and rhs[k]==v for k,v in lhs.items()),
   "solo_operativo":sum(k not in lhs for k in rhs)}
 return result

def simulacion(source,operativo,politica="solo_insertar"):
 """La tabla de destino debe ser copia LOCAL de pruebas, nunca Sheets.
 Modificados se dejan intactos mientras no exista precedencia por campo.
 """
 if politica!="solo_insertar":raise ValueError("Política de cambios no autorizada")
 antes=plan_local(source,operativo)
 for table in TABLES:
  for pk,raw in source.execute('SELECT pk,fila FROM "'+table+'"'):
   operativo.execute('INSERT OR IGNORE INTO "'+table+'" (pk,fila) VALUES (?,?)',(pk,raw))
 operativo.commit()
 despues=plan_local(source,operativo)
 for t in TABLES:
  if despues[t]["nuevos"]!=0:raise ValueError("Falla de simulación de altas en "+t)
  if despues[t]["modificados"]!=antes[t]["modificados"]:
   raise ValueError("Se modificaron registros preexistentes en "+t)
  if despues[t]["solo_operativo"]!=antes[t]["solo_operativo"]:
   raise ValueError("Se perdieron registros operativos de "+t)
 return antes,despues

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--paquete",type=Path,required=True)
 p.add_argument("--conciliacion",type=Path,required=True)
 p.add_argument("--plan",type=Path,required=True)
 p.add_argument("--salida",type=Path)
 args=p.parse_args()
 plan=json.loads(args.plan.read_text(encoding="utf8"))
 conciliacion=json.loads(args.conciliacion.read_text(encoding="utf8"))
 if plan.get("autorizado_para_escribir") is not False or plan.get("autorizado_para_mover") is not False:
  p.error("Plan inesperadamente autorizado; detención preventiva")
 if conciliacion.get("periodo")!=plan.get("periodo"):p.error("Períodos diferentes")
 paquete=args.paquete
 manifest=json.loads((paquete/"informe.json").read_text(encoding="utf8"))
 if manifest.get("periodo")!=plan["periodo"] or manifest.get("validacion_filas")!="OK":
  p.error("Paquete incompatible")
 for table in TABLES:
  if table not in manifest or not (paquete/(table+".csv")).is_file():
   p.error("Falta CSV o conteo "+table)
 # La simulación de escritura usa una copia SQLite local, sin usar Google.
 fuente=sqlite3.connect(f"file:{(paquete/'preparado.sqlite').resolve()}?mode=ro",uri=True)
 out=args.salida or paquete.parent/"simulacion_motor_carga.json"
 out.parent.mkdir(parents=True,exist_ok=True)
 for table in TABLES:
  n=fuente.execute('SELECT COUNT(*) FROM "'+table+'"').fetchone()[0]
  if n!=manifest[table]:p.error("Recuento inconsistente en "+table)
 resultado={"periodo":plan["periodo"],"fecha_chile":dt.datetime.now(ZoneInfo("America/Santiago")).isoformat(),
  "estado":"MOTOR_CARGA_SIMULADO_SIN_CONEXION_GOOGLE",
  "politica":"insertar solo claves nuevas; no modificar ni borrar existentes",
  "huellas_csv":{t:digest(paquete/(t+".csv")) for t in TABLES},
  "candidatos":plan["acciones_candidatas"],
  "escritura_google":False,"traslado_drive":False,
  "pendiente":"Ensayo en SQLite local y cargador Google con auditoría/aprobación explícita"}
 out.write_text(json.dumps(resultado,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 fuente.close()
 print("SIMULACION SIN ESCRITURAS:",out)

if __name__=="__main__":main()
