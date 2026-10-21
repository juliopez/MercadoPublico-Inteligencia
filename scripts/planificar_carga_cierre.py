#!/usr/bin/env python3
"""Política y plan de carga de cierre MER v2. EXCLUSIVAMENTE SOLO LECTURA.

Lee el informe de conciliación (sin conectarse a Google). Nunca escribe Sheets.
Los cambios requieren revisión humana de diferencias, validación referencial y
respaldo previo. La propuesta es conservadora: ningún borrado ni traslado.
"""
import argparse,json,datetime as dt
from pathlib import Path
from zoneinfo import ZoneInfo

TABLAS=("Procesos","Ofertas","Resultados","OrdenesCompra","Proveedores","VinculosCOT_OC")
def evaluar(informe):
 if informe.get("estado")!="CONCILIACION_INFORMATIVA_REQUIERE_REVISION":
  raise ValueError("Informe de conciliación no válido")
 filas=informe.get("tablas",{})
 if set(filas)!=set(TABLAS):raise ValueError("Deben conciliarse las seis tablas MER v2")
 acciones={};alertas=[]
 for tabla in TABLAS:
  datos=filas[tabla]
  counts={k:datos.get(k) for k in ("nuevos","modificados","sin_cambios","solo_operativo")}
  if any(not isinstance(v,int) or v<0 for v in counts.values()):
   raise ValueError("Conteos inválidos en "+tabla)
  if counts["nuevos"]+counts["modificados"]+counts["sin_cambios"]!=datos.get("filas_historico"):
   raise ValueError("Inconsistencia del histórico en "+tabla)
  if counts["modificados"]+counts["sin_cambios"]+counts["solo_operativo"]!=datos.get("filas_operativo"):
   raise ValueError("Inconsistencia del operativo en "+tabla)
  acciones[tabla]={"insertar_candidatos":counts["nuevos"],
    "actualizar_candidatos_sujetos_a_revision":counts["modificados"],
    "conservar":counts["sin_cambios"],"solo_operativo_sin_borrado":counts["solo_operativo"]}
  if counts["modificados"]:
   alertas.append(f"{tabla}: {counts['modificados']} valores diferentes, requieren política campo a campo")
  if counts["solo_operativo"]:
   alertas.append(f"{tabla}: {counts['solo_operativo']} registros solo operativos, no deben eliminarse")
 # Las selecciones históricas no se convierten automáticamente en adjudicaciones.
 notas=informe.get("observaciones_paquete",{})
 for k,v in notas.items():
  if isinstance(v,int) and v>0:
   alertas.append(f"Observación histórica {k}: {v}; exige interpretación antes de cierre")
 return {"periodo":informe["periodo"],"spreadsheet_id":informe["spreadsheet_id"],
  "estado":"PLAN_DE_CARGA_BLOQUEADO_HASTA_AUDITORIA_Y_APROBACION",
  "fecha_chile":dt.datetime.now(ZoneInfo("America/Santiago")).isoformat(),
  "acciones_candidatas":acciones,"alertas":alertas,
  "politicas":{
   "nuevos":"Candidatos a inserción por PK, luego de auditoría",
   "modificados":"No sobrescribir sin revisión por tabla y campo; no elevar selecciones históricas a adjudicaciones confirmadas",
   "sin_cambios":"No escribir",
   "solo_operativo":"Preservar; nunca eliminar por mera ausencia del ZIP",
   "vinculos_fuera_periodo":"No asumir error por OC fuera del mes",
   "fuente_oficial":"Prioridad sujeta a revisión de cobertura y trazabilidad",
   "cierre":"No habilitado sin respaldo verificado, auditoría aprobada y comprobación post-carga"},
  "autorizado_para_escribir":False,"autorizado_para_mover":False}
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--conciliacion",type=Path,required=True)
 p.add_argument("--salida",type=Path)
 args=p.parse_args()
 data=json.loads(args.conciliacion.read_text(encoding="utf-8"))
 resultado=evaluar(data)
 salida=args.salida or args.conciliacion.parent/"plan_carga_cierre.json"
 salida.parent.mkdir(parents=True,exist_ok=True)
 salida.write_text(json.dumps(resultado,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(resultado,ensure_ascii=False,indent=2))
 print("PLAN",salida)
if __name__=="__main__":main()
