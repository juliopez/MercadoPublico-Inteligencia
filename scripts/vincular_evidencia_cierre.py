#!/usr/bin/env python3
"""Vincula preparación, conciliación y plan a evidencia inmutable SHA-256.

No solicita credenciales, no conecta a Google ni permite escribir.
Detecta sustitución de archivos o informes desde su inspección.
"""
import argparse,hashlib,json,datetime as dt
from pathlib import Path
from zoneinfo import ZoneInfo
TABLES=("Procesos","Ofertas","Resultados","OrdenesCompra","Proveedores","VinculosCOT_OC")
def sha(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
 return h.hexdigest()
def verificar(periodo,paquete,conciliacion,plan,catalogo,estado):
 ci=json.loads(conciliacion.read_text(encoding="utf8"))
 pl=json.loads(plan.read_text(encoding="utf8"))
 ca=json.loads(catalogo.read_text(encoding="utf8"))
 es=json.loads(estado.read_text(encoding="utf8"))
 report_path=paquete/"informe.json"
 rep=json.loads(report_path.read_text(encoding="utf8"))
 item=ca["periodos"].get(periodo)
 if not item or item.get("tipo")!="operativo":raise ValueError("Período ya no es operativo")
 if any(d.get("periodo")!=periodo for d in (ci,pl,es,rep)):raise ValueError("Período divergente")
 if item["id"]!=ci["spreadsheet_id"] or item["id"]!=pl["spreadsheet_id"] or item["id"]!=es["hoja_operativa_origen"]:
  raise ValueError("ID de hoja divergente")
 if ci.get("estado")!="CONCILIACION_INFORMATIVA_REQUIERE_REVISION":raise ValueError("Conciliación inválida")
 if pl.get("estado")!="PLAN_DE_CARGA_BLOQUEADO_HASTA_AUDITORIA_Y_APROBACION":raise ValueError("Plan inválido")
 if es.get("estado")!="LISTO_PARA_CONCILIAR" or rep.get("validacion_filas")!="OK":raise ValueError("Preparación incompleta")
 if pl.get("autorizado_para_escribir") is not False or pl.get("autorizado_para_mover") is not False:
  raise ValueError("Permisos inesperados en el plan")
 for t in TABLES:
  c=ci["tablas"][t];p=pl["acciones_candidatas"][t]
  if c["filas_historico"]!=rep[t] or c["nuevos"]!=p["insertar_candidatos"] or c["modificados"]!=p["actualizar_candidatos_sujetos_a_revision"] or c["solo_operativo"]!=p["solo_operativo_sin_borrado"]:
   raise ValueError("Conteos divergentes en "+t)
 if set(pl["acciones_candidatas"])!=set(TABLES):raise ValueError("Faltan tablas")
 required=[report_path,paquete/"preparado.sqlite",conciliacion,plan,estado,catalogo]
 required += [paquete/(t+".csv") for t in TABLES]
 for f in required:
  if not f.is_file():raise ValueError("Archivo ausente "+str(f))
 return {"periodo":periodo,"sheet_id":item["id"],
         "generado_chile":dt.datetime.now(ZoneInfo("America/Santiago")).isoformat(),
         "estado":"EVIDENCIA_VINCULADA_SIN_APROBACION",
         "archivos":{str(f.resolve()):{"bytes":f.stat().st_size,"sha256":sha(f)} for f in required},
         "escritura_autorizada":False,"traslado_autorizado":False,
         "pendiente":"Auditoría de contenido, aprobación de cambios, preflight remoto, respaldo y recuperación"}
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--periodo",required=True)
 p.add_argument("--paquete",required=True,type=Path)
 p.add_argument("--conciliacion",required=True,type=Path)
 p.add_argument("--plan",required=True,type=Path)
 p.add_argument("--estado",required=True,type=Path)
 p.add_argument("--catalogo",type=Path,default=Path(__file__).resolve().parents[1]/"config/catalogo_sheets.json")
 p.add_argument("--salida",type=Path)
 a=p.parse_args()
 result=verificar(a.periodo,a.paquete,a.conciliacion,a.plan,a.catalogo,a.estado)
 output=a.salida or a.paquete.parent/"evidencia_vinculada.json"
 output.parent.mkdir(parents=True,exist_ok=True)
 output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print("EVIDENCIA VINCULADA, NO APROBADA:",output)
if __name__=="__main__":main()
