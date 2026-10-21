#!/usr/bin/env python3
"""Adaptadores inyectables para cierre Drive/GitHub. CLI de producción DESACTIVADA.

Funciones move_drive/update_catalog deben proporcionarse explícitamente
por una futura capa autenticada, después de una aprobación del cierre.
Nunca crea ni duplica un archivo; conserva sheet ID.
"""
import copy,json
from pathlib import Path
def verificar_drive(fileinfo,plan,destino=False):
 expected=plan["despues" if destino else "antes"]
 if fileinfo.get("id")!=plan["id_original"]:raise ValueError("ID Drive inesperado")
 if fileinfo.get("nombre")!=expected["nombre"] or fileinfo.get("carpeta")!=expected["carpeta"]:
  raise ValueError("Ubicación o nombre Drive inesperado")
def cambio_catalogo(catalog,plan):
 result=copy.deepcopy(catalog)
 p=plan["periodo"];item=result["periodos"][p]
 if item.get("id")!=plan["id_original"] or item.get("tipo")!="operativo":
  raise ValueError("Catálogo cambió desde la preparación")
 item["tipo"]="historico"
 item["estado"]="auditado_con_observaciones"
 # Conteo se establece desde informe de auditoría final, no se conserva el de octubre.
 item.pop("filas",None)
 return result
def ejecutar(plan,leer_drive,leer_catalogo,mover_drive,guardar_catalogo,registrar,autorizar=False):
 """Core para ensayos con dobles. NO se conecta a APIs por sí mismo."""
 if not autorizar:raise PermissionError("Traslado no autorizado")
 if plan.get("estado")!="SIMULACION_SIN_TRASLADO":
  raise ValueError("Plan inválido")
 catalog=leer_catalogo();info=leer_drive(plan["id_original"])
 entry=catalog["periodos"].get(plan["periodo"],{})
 if entry.get("id")!=plan["id_original"]:raise ValueError("Catálogo ID distinto")
 from protocolo_traslado_drive_github import paso
 status=paso(plan,info,catalog,"PREPARADO")["situacion"]
 if status=="INCONSISTENCIA_CATALOGO_ADELANTADO":raise ValueError("Catálogo adelantado")
 if status=="PENDIENTE_MOVER_DRIVE":
  verificar_drive(info,plan)
  registrar("INTENCION_TRASLADO",plan)
  mover_drive(plan["id_original"],plan["antes"]["carpeta"],plan["despues"]["carpeta"],plan["despues"]["nombre"])
  info=leer_drive(plan["id_original"])
  verificar_drive(info,plan,destino=True)
  registrar("DRIVE_CONFIRMADO",plan)
 elif status=="PENDIENTE_ACTUALIZAR_CATALOGO":
  verificar_drive(info,plan,destino=True)
 if status!="FINALIZADO":
  catalog=leer_catalogo()
  if catalog["periodos"][plan["periodo"]]["tipo"]=="operativo":
   guardar_catalogo(cambio_catalogo(catalog,plan))
   registrar("CATALOGO_CONFIRMADO",plan)
 final=paso(plan,leer_drive(plan["id_original"]),leer_catalogo(),"FINALIZADO")
 if final["situacion"]!="FINALIZADO":raise ValueError("Traslado incompleto")
 registrar("FINALIZADO",plan)
 return final
def main():
 raise SystemExit("BLOQUEADO: adaptadores reales deshabilitados hasta cierre supervisado y validado")
if __name__=="__main__":main()
