#!/usr/bin/env python3
"""Protocolo de traslado MER: máquina de estados, SIN llamadas a Drive/GitHub.

Los adaptadores reales no están conectados. Permite ensayar que una interrupción
después de mover en Drive NO repite movimiento y solicita reparación del catálogo.
"""
import argparse,json,datetime as dt
from pathlib import Path
from zoneinfo import ZoneInfo
STATES=("PREPARADO","DRIVE_CONFIRMADO","CATALOGO_CONFIRMADO","FINALIZADO")
def paso(plan,metadatos,catalogo,etapa):
 if plan.get("estado")!="SIMULACION_SIN_TRASLADO":raise ValueError("Plan no es simulación válida")
 pid=plan["id_original"];p=plan["periodo"];old=plan["antes"];new=plan["despues"]
 if metadatos.get("id")!=pid:raise ValueError("ID Drive incorrecto")
 current=catalogo["periodos"].get(p)
 if not current or current.get("id")!=pid:raise ValueError("ID catálogo incorrecto")
 src=metadatos.get("nombre")==old["nombre"] and metadatos.get("carpeta")==old["carpeta"]
 dst=metadatos.get("nombre")==new["nombre"] and metadatos.get("carpeta")==new["carpeta"]
 if not src and not dst:raise ValueError("Drive en ubicación imprevista: intervención manual")
 oldcat=current.get("tipo")=="operativo";newcat=current.get("tipo")=="historico"
 if not oldcat and not newcat:raise ValueError("Catálogo en estado imprevisto")
 if src and oldcat:accion="PENDIENTE_MOVER_DRIVE"
 elif dst and oldcat:accion="PENDIENTE_ACTUALIZAR_CATALOGO"
 elif dst and newcat:accion="FINALIZADO"
 else:accion="INCONSISTENCIA_CATALOGO_ADELANTADO"
 if etapa=="FINALIZADO" and accion!="FINALIZADO":raise ValueError("Cierre marcado final sin consistencia")
 return {"periodo":p,"sheet_id":pid,"situacion":accion,
  "siguiente_accion":accion,"autorizado_para_ejecutar":False,
  "orden":"Solo después de aprobación independiente, Drive primero, catálogo después"}
def main():
 a=argparse.ArgumentParser()
 a.add_argument("--plan",type=Path,required=True)
 a.add_argument("--metadata-drive",type=Path,required=True,help="Snapshot metadatos controlado, no consulta en vivo")
 a.add_argument("--catalogo",type=Path,required=True)
 a.add_argument("--estado",default="PREPARADO",choices=STATES)
 a.add_argument("--salida",type=Path)
 v=a.parse_args()
 obj=paso(json.loads(v.plan.read_text()),json.loads(v.metadata_drive.read_text()),json.loads(v.catalogo.read_text()),v.estado)
 obj["fecha_chile"]=dt.datetime.now(ZoneInfo("America/Santiago")).isoformat()
 out=v.salida or v.plan.parent/"simulacion_recuperacion_traslado.json"
 out.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print(json.dumps(obj,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
