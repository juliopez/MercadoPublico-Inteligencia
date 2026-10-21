#!/usr/bin/env python3
"""Evaluación final MER v2: SOLO LECTURA, NUNCA AUTORIZA TRASLADO.

Reúne evidencias del cierre y detecta bloqueos; una evaluación favorable
solo constituye candidato a aprobación supervisada, no autorización operativa.
"""
import argparse,datetime as dt,json
from pathlib import Path
from zoneinfo import ZoneInfo

def evaluar(periodo,catalogo,preparacion,conciliacion,plan,auditoria,revalidacion,carga):
 motivos=[]
 entry=catalogo.get("periodos",{}).get(periodo)
 if not entry or entry.get("tipo")!="operativo":motivos.append("Mes no está catalogado como operativo")
 sid=entry.get("id") if entry else None
 def coincide(nombre,obj):
  if obj.get("periodo")!=periodo:motivos.append(nombre+": período inconsistente")
 for name,obj in (("preparacion",preparacion),("conciliacion",conciliacion),("plan",plan),
                  ("auditoria",auditoria),("revalidacion",revalidacion),("carga",carga)):
  coincide(name,obj)
 if preparacion.get("estado")!="LISTO_PARA_CONCILIAR":motivos.append("Los tres ZIP oficiales no están preparados")
 if conciliacion.get("estado")!="CONCILIACION_INFORMATIVA_REQUIERE_REVISION":
  motivos.append("Falta conciliación completa")
 if plan.get("estado")!="PLAN_DE_CARGA_BLOQUEADO_HASTA_AUDITORIA_Y_APROBACION":
  motivos.append("Plan de diferencias ausente o inválido")
 if auditoria.get("estado")!="AUDITORIA_ESTRUCTURAL_SIN_ERRORES_CON_OBSERVACIONES":
  motivos.append("Auditoría estructural no aprobada")
 if auditoria.get("errores_bloqueantes"):motivos.append("Existen errores referenciales bloqueantes")
 if revalidacion.get("estado")!="OPERATIVO_SIN_CAMBIOS_DESDE_CONCILIACION":
  motivos.append("No consta revalidación del operativo")
 if carga.get("estado")!="DATOS_CARGADOS_Y_VERIFICADOS_PENDIENTES_DE_AUDITORIA":
  motivos.append("No consta la carga real y lectura posterior de las seis tablas")
 if not carga.get("respaldo",{}).get("sha256"):motivos.append("No consta respaldo verificable")
 if sid:
  for name,obj in (("conciliacion",conciliacion),("revalidacion",revalidacion),("carga",carga)):
   if obj.get("spreadsheet_id")!=sid:motivos.append(name+": identificador Sheets distinto")
 if preparacion.get("hoja_operativa_origen")!=sid:motivos.append("Destino de preparación distinto")
 if plan.get("spreadsheet_id")!=sid:motivos.append("Destino del plan distinto")
 tablas=("Procesos","Ofertas","Resultados","OrdenesCompra","Proveedores","VinculosCOT_OC")
 for name,obj,field in (("conciliacion",conciliacion,"tablas"),("auditoria",auditoria,"conteos"),
                        ("revalidacion",revalidacion,"tablas"),("carga",carga,"tablas")):
  if set(obj.get(field,{}))!=set(tablas):motivos.append(name+": faltan tablas")
 if plan.get("autorizado_para_escribir") is not False or plan.get("autorizado_para_mover") is not False:
  motivos.append("Plan de diferencias tiene permisos inesperados")
 if auditoria.get("observaciones"):motivos.append("Existen observaciones que requieren revisión documentada")
 return {"periodo":periodo,"estado":"BLOQUEADO" if motivos else "CANDIDATO_A_APROBACION_SUPERVISADA",
         "motivos":motivos,"cierre_autorizado":False,"traslado_autorizado":False,
         "escrituras_google":False,
         "advertencia":"El informe no autoriza por sí mismo operaciones Drive ni actualizaciones GitHub."}
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--periodo",required=True)
 p.add_argument("--directorio",type=Path,required=True)
 p.add_argument("--catalogo",type=Path,default=Path(__file__).resolve().parents[1]/"config/catalogo_sheets.json")
 a=p.parse_args()
 required={"preparacion":"estado_cierre.json","conciliacion":"conciliacion.json","plan":"plan_carga_cierre.json",
 "auditoria":"auditoria_referencial.json","revalidacion":"revalidacion_operativo.json","carga":"carga_verificada.json"}
 data={}
 for key,name in required.items():
  f=a.directorio/name
  if not f.is_file():data[key]={"periodo":a.periodo,"estado":"AUSENTE"}
  else:data[key]=json.loads(f.read_text(encoding="utf8"))
 catalog=json.loads(a.catalogo.read_text(encoding="utf8"))
 result=evaluar(a.periodo,catalog,**data)
 result["fecha_chile"]=dt.datetime.now(ZoneInfo("America/Santiago")).isoformat()
 path=a.directorio/"evaluacion_final_cierre.json"
 path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
