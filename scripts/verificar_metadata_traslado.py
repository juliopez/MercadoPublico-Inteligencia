#!/usr/bin/env python3
"""Verificación de metadatos Drive vs catálogo MER. Solo lectura.

No solicita tokens adicionales ni escribe. Consume un snapshot JSON obtenido
por el propietario y el catálogo vigente. No autoriza ni ejecuta traslados.
"""
import argparse,datetime as dt,json
from pathlib import Path
from zoneinfo import ZoneInfo

def comprobar(periodo,catalogo,metadata):
 obj=catalogo.get("periodos",{}).get(periodo)
 issues=[]
 if not obj or obj.get("tipo")!="operativo":issues.append("PERIODO_NO_OPERATIVO")
 id_=obj.get("id") if obj else None
 if not id_ or metadata.get("id")!=id_:issues.append("ID_DIVERGENTE")
 origen=catalogo.get("carpetas",{}).get("operativo")
 esperado="MER_"+periodo.replace("-","_")+"_OPERATIVO"
 if metadata.get("title")!=esperado:issues.append("NOMBRE_DIVERGENTE")
 parents=metadata.get("parent_ids") or []
 if origen not in parents or len(parents)!=1:issues.append("CARPETA_DIVERGENTE")
 if metadata.get("mime_type")!="application/vnd.google-apps.spreadsheet":
  issues.append("TIPO_ARCHIVO_INCORRECTO")
 perms=metadata.get("permissions")
 if perms is None:issues.append("PERMISOS_NO_VERIFICABLES")
 else:
  for perm in perms:
   if perm.get("type") in ("anyone","domain") and perm.get("role") in ("writer","owner"):
    issues.append("EDICION_GENERAL_NO_RESTRINGIDA")
 return {"periodo":periodo,"spreadsheet_id":id_,"estado":"BLOQUEADO" if issues else "METADATOS_CONSISTENTES",
         "alertas":issues,"escrituras_drive":False,"escrituras_github":False,
         "traslado_autorizado":False}
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--periodo",required=True)
 p.add_argument("--metadata-drive",type=Path,required=True)
 p.add_argument("--catalogo",type=Path,default=Path(__file__).resolve().parents[1]/"config/catalogo_sheets.json")
 p.add_argument("--salida",type=Path)
 a=p.parse_args()
 result=comprobar(a.periodo,json.loads(a.catalogo.read_text(encoding="utf8")),
  json.loads(a.metadata_drive.read_text(encoding="utf8")))
 result["fecha_chile"]=dt.datetime.now(ZoneInfo("America/Santiago")).isoformat()
 if a.salida:
  a.salida.parent.mkdir(parents=True,exist_ok=True)
  a.salida.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
