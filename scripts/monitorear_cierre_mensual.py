#!/usr/bin/env python3
"""Monitor de cierre mensual MER v2 (SOLO LECTURA / SIN CIERRE).
Comprueba ZIP COT del mes anterior y estado del catálogo, sin cambiar hojas.
"""
import argparse,datetime as dt,json,urllib.request,urllib.error
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
def anterior(hoy):
 primero=hoy.replace(day=1)
 return (primero-dt.timedelta(days=1)).strftime("%Y-%m")
def disponibilidad(url):
 try:
  req=urllib.request.Request(url,method="HEAD",headers={"User-Agent":"MER-v2-close-watch/1.0"})
  with urllib.request.urlopen(req,timeout=35) as r:
   return {"http":r.status,"disponible":r.status==200,"bytes":r.headers.get("Content-Length"),"last_modified":r.headers.get("Last-Modified")}
 except urllib.error.HTTPError as e:return {"http":e.code,"disponible":False,"error":str(e.reason)}
 except Exception as e:return {"http":None,"disponible":False,"error":str(e)}
def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--periodo",help="Solo período anterior a mes vigente (AAAA-MM)")
 args=parser.parse_args()
 hoy=dt.datetime.now(ZoneInfo("America/Santiago"))
 prev=anterior(hoy)
 if args.periodo and args.periodo!=prev:parser.error("Solo está permitido revisar el mes calendario anterior: "+prev)
 year,month=prev.split("-")
 config=json.loads((ROOT/"config/fuentes_descarga_mensual.json").read_text(encoding="utf8"))
 catalog=json.loads((ROOT/"config/catalogo_sheets.json").read_text(encoding="utf8"))
 old=catalog["periodos"].get(prev)
 new=catalog["periodos"].get(hoy.strftime("%Y-%m"))
 fuentes={}
 for k,pattern in config["fuentes"].items():
  url=pattern.format(yyyy=year,mm=month)
  fuentes[k]={"url":url,**disponibilidad(url)}
 estado="FUENTES_DISPONIBLES_REVISION_MANUAL_PENDIENTE" if all(f["disponible"] for f in fuentes.values()) else "ESPERANDO_FUENTES"
 if not old or not new:estado="CATALOGO_INCOMPLETO"
 reporte={"momento_chile":hoy.isoformat(),"periodo_candidato":prev,
          "periodo_operativo_actual":hoy.strftime("%Y-%m"),"estado":estado,
          "catalogo_anterior":old,"catalogo_actual":new,"fuentes":fuentes,
          "cierre_ejecutado":False,"escrituras_google_sheets":False,
          "acciones_pendientes":["Preparar y auditar ZIP de las 3 fuentes del mes saliente",
                                "Conciliar y validar seis tablas MER v2",
                                "Aprobar el cierre antes de mover/renombrar la hoja",
                                "Registrar evidencia y actualizar catálogo"]}
 out=ROOT/"salida_operativa";out.mkdir(exist_ok=True)
 path=out/("cierre_candidato_"+prev+".json")
 path.write_text(json.dumps(reporte,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print(json.dumps(reporte,ensure_ascii=False,indent=2))
 print("Informe:",path)
if __name__=="__main__":main()
