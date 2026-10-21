#!/usr/bin/env python3
"""Plan de traslado MER v2 SOLO SIMULACIÓN; nunca llama Drive ni GitHub.

El movimiento real deberá hacer update_file de metadatos, conservando el ID,
y actualizar el catálogo solo tras comprobar la ubicación. No se autoriza aquí.
"""
import argparse,datetime as dt,json
from pathlib import Path
from zoneinfo import ZoneInfo

def planificar(periodo,catalogo,evaluacion):
 entry=catalogo.get("periodos",{}).get(periodo)
 if not entry or entry.get("tipo")!="operativo" or not entry.get("id"):
  raise ValueError("Período no operativo o sin identificador")
 if entry["id"] in set(catalogo.get("excluidos",{}).values()):
  raise ValueError("ID excluido; traslado prohibido")
 if evaluacion.get("periodo")!=periodo:raise ValueError("Evaluación de otro período")
 if evaluacion.get("estado")!="CANDIDATO_A_APROBACION_SUPERVISADA":
  raise ValueError("No hay evaluación favorable")
 if evaluacion.get("cierre_autorizado") is not False or evaluacion.get("traslado_autorizado") is not False:
  raise ValueError("Evaluación inesperadamente autoriza traslado")
 carpetas=catalogo.get("carpetas",{})
 if not carpetas.get("operativo") or not carpetas.get("historicos") or carpetas["operativo"]==carpetas["historicos"]:
  raise ValueError("Carpetas ausentes o idénticas")
 nombre="MER_"+periodo.replace("-","_")
 return {"periodo":periodo,"id_original":entry["id"],
         "antes":{"nombre":nombre+"_OPERATIVO","carpeta":carpetas["operativo"],"tipo":"operativo"},
         "despues":{"nombre":nombre,"carpeta":carpetas["historicos"],"tipo":"historico"},
         "orden_futuro":["Preflight y aprobación independiente",
            "Registrar transacción durable e ID de origen",
            "Verificar nombre y carpeta reales desde Google Drive",
            "Mover mismo ID entre carpetas y renombrar",
            "Comprobar Drive: nombre/parent/ID",
            "Actualizar catálogo en GitHub preservando mismo ID",
            "Comprobar GitHub y registrar resultado"],
         "recuperacion":{"drive_cambiado_catalogo_antiguo":"Verificar estado en Drive; reintentar solo transición de catálogo",
            "drive_sin_cambiar":"Conservar catálogo operativo, bloquear cierre",
            "catalogo_cambiado_drive_antiguo":"Detener y corregir con auditoría, no ejecutar traslado ciego"},
         "estado":"SIMULACION_SIN_TRASLADO",
         "autorizado_para_mover":False,"autorizado_para_actualizar_catalogo":False}
def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--periodo",required=True)
 parser.add_argument("--evaluacion",required=True,type=Path)
 parser.add_argument("--catalogo",type=Path,default=Path(__file__).resolve().parents[1]/"config/catalogo_sheets.json")
 parser.add_argument("--salida",type=Path)
 args=parser.parse_args()
 cat=json.loads(args.catalogo.read_text(encoding="utf8"))
 evaluacion=json.loads(args.evaluacion.read_text(encoding="utf8"))
 result=planificar(args.periodo,cat,evaluacion)
 result["fecha_chile"]=dt.datetime.now(ZoneInfo("America/Santiago")).isoformat()
 dest=args.salida or args.evaluacion.parent/"simulacion_traslado.json"
 dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
