#!/usr/bin/env python3
"""Simulación bloqueante del cargador histórico MER v2.

Lee el SQLite preparado y el plan de conciliación. No abre Google Sheets,
no ejecuta escrituras, no cambia metadatos Drive ni catálogo GitHub.
"""
import argparse,datetime as dt,hashlib,json,sqlite3
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
TABLAS=("Procesos","Ofertas","Resultados","OrdenesCompra","Proveedores","VinculosCOT_OC")
def digest(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
 return h.hexdigest()
def preflight(periodo,paquete,plan,estado,catalogo):
 if plan.get("periodo")!=periodo or estado.get("periodo")!=periodo:
  raise ValueError("Períodos inconsistentes entre paquete y reportes")
 entry=catalogo["periodos"].get(periodo)
 if not entry or entry.get("tipo")!="operativo":
  raise ValueError("El destino no figura como operativo en catálogo")
 if plan.get("spreadsheet_id")!=entry["id"] or estado.get("hoja_operativa_origen")!=entry["id"]:
  raise ValueError("ID operativo distinto entre catálogo, conciliación y preparación")
 if estado.get("estado")!="LISTO_PARA_CONCILIAR":
  raise ValueError("La preparación no está completa")
 if plan.get("autorizado_para_escribir") is not False or plan.get("autorizado_para_mover") is not False:
  raise ValueError("Plan inesperadamente autoriza una operación: revisar")
 if plan.get("estado")!="PLAN_DE_CARGA_BLOQUEADO_HASTA_AUDITORIA_Y_APROBACION":
  raise ValueError("Plan no es de la versión bloqueante conocida")
 acciones=plan.get("acciones_candidatas",{})
 if set(acciones)!=set(TABLAS):raise ValueError("Faltan entidades MER v2")
 dbpath=paquete/"preparado.sqlite"
 report=json.loads((paquete/"informe.json").read_text(encoding="utf-8"))
 if report.get("periodo")!=periodo or report.get("validacion_filas")!="OK":
  raise ValueError("Informe oficial inválido")
 db=sqlite3.connect(f"file:{dbpath.resolve()}?mode=ro",uri=True)
 try:
  conteos={}
  for t in TABLAS:
   c=db.execute('SELECT COUNT(*) FROM "'+t+'"').fetchone()[0]
   esperado=acciones[t]["insertar_candidatos"]+acciones[t]["actualizar_candidatos_sujetos_a_revision"]+acciones[t]["conservar"]
   if c!=esperado or c!=report[t]:
    raise ValueError("Descuadre de registros en "+t)
   path=paquete/(t+".csv")
   if not path.is_file():raise ValueError("Falta CSV: "+t)
   conteos[t]={"filas_oficiales":c,"csv_sha256":digest(path),
               "insertar_candidatos":acciones[t]["insertar_candidatos"],
               "actualizar_candidatos":acciones[t]["actualizar_candidatos_sujetos_a_revision"],
               "solo_operativo_conservar":acciones[t]["solo_operativo_sin_borrado"]}
  return {"periodo":periodo,"spreadsheet_id":entry["id"],
   "fecha_chile":dt.datetime.now(ZoneInfo("America/Santiago")).isoformat(),
   "estado":"SIMULACION_SIN_ESCRITURAS_BLOQUEADA",
   "tablas":conteos,
   "controles_pendientes":["Conciliación campo a campo y auditoría referencial final",
     "Verificar límite de celdas según hoja destino",
     "Respaldo integral con CRC y SHA256 antes de aplicar",
     "Aprobación documentada de diferencias y conservación de solo-operativos",
     "Implementar cargador idempotente y read-back después de cada tabla",
     "Ensayar recuperación de fallos antes de automatizar",
     "Verificar permisos Drive y traslado del mismo spreadsheet ID",
     "Actualizar catálogo de forma recuperable"],
   "escrituras_google_sheets":False,"traslado_drive":False,
   "nota":"Este script nunca escribe, aunque el usuario proporcione una bandera de aplicación."}
 finally:db.close()
def main():
 parser=argparse.ArgumentParser(description="Preflight sin escrituras del cierre")
 parser.add_argument("--periodo",required=True)
 parser.add_argument("--paquete",type=Path,required=True)
 parser.add_argument("--plan",type=Path,required=True)
 parser.add_argument("--estado",type=Path,required=True)
 parser.add_argument("--salida",type=Path)
 args=parser.parse_args()
 catalogo=json.loads((ROOT/"config/catalogo_sheets.json").read_text(encoding="utf-8"))
 plan=json.loads(args.plan.read_text(encoding="utf-8"))
 estado=json.loads(args.estado.read_text(encoding="utf-8"))
 resultado=preflight(args.periodo,args.paquete,plan,estado,catalogo)
 salida=args.salida or args.paquete.parent/"simulacion_carga_cierre.json"
 salida.parent.mkdir(parents=True,exist_ok=True)
 salida.write_text(json.dumps(resultado,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(resultado,ensure_ascii=False,indent=2))
 print("INFORME",salida)
if __name__=="__main__":main()
