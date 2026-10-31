#!/usr/bin/env python3
"""Un único comando para PREPARAR y DIAGNOSTICAR el cierre mensual MER v2.

Ejecuta componentes existentes; NO escribe Google Sheets, NO mueve Drive,
NO actualiza GitHub y NO activa cron. Los errores detienen la secuencia.
Ejecutar a partir del día 10, únicamente con el mes anterior.
"""
import argparse,datetime as dt,json,os,subprocess,sys
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
def periodo_anterior(now):
 return (now.date().replace(day=1)-dt.timedelta(days=1)).strftime("%Y-%m")
def ejecutar(argv,base,env):
 print("ETAPA:",argv[1],flush=True)
 subprocess.run([sys.executable,*argv],cwd=ROOT,env=env,check=True)
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--periodo",help="Solo período inmediatamente anterior")
 p.add_argument("--directorio",type=Path,default=Path.home()/".local/share/mercadopublico/cierres")
 args=p.parse_args()
 now=dt.datetime.now(ZoneInfo("America/Santiago"))
 period=periodo_anterior(now)
 if args.periodo and args.periodo!=period:p.error("Solo se prepara el mes anterior "+period)
 if now.day<10:p.error("El cierre se prepara desde el día 10")
 home=args.directorio.expanduser().resolve()/period
 home.mkdir(parents=True,exist_ok=True)
 prepared=home/"preparados";oper=home/"operativo_snapshot.sqlite"
 commands=[
  ["scripts/orquestar_cierre_mensual.py","--periodo",period,"--directorio",str(args.directorio.expanduser().resolve())],
  ["scripts/exportar_operativo_sqlite.py","--periodo",period,"--salida",str(oper)],
  ["scripts/conciliar_cierre_mensual.py","--periodo",period,"--paquete",str(prepared)],
  ["scripts/planificar_carga_cierre.py","--conciliacion",str(home/"conciliacion.json")],
  ["scripts/auditar_referencias_cierre.py","--paquete",str(prepared)],
  ["scripts/auditar_diferencias_campos_cierre.py","--oficial",str(prepared/"preparado.sqlite"),"--operativo-snapshot",str(oper),"--salida",str(home/"diferencias_por_campo.json")],
  ["scripts/politica_conciliacion_cierre.py","--oficial",str(prepared/"preparado.sqlite"),"--operativo-snapshot",str(oper),"--salida",str(home/"politica_conciliacion.json")],
 ]
 report={"periodo":period,"inicio_chile":now.isoformat(),"estado":"EN_CURSO",
         "etapas":[],"escrituras_google_sheets":False,"traslado_drive":False,"cron_instalado":False}
 path=home/"resumen_diagnostico_cierre.json"
 def save():
  path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 env=os.environ.copy()
 env.setdefault("GOOGLE_APPLICATION_CREDENTIALS",str(Path.home()/".config/mercadopublico/servicio-google.json"))
 try:
  for cmd in commands:
   name=Path(cmd[0]).stem
   ejecutar(cmd,home,env)
   report["etapas"].append({"etapa":name,"resultado":"OK"})
   save()
  polic=json.loads((home/"politica_conciliacion.json").read_text(encoding="utf8"))
  report["conflictos_totales"]=polic.get("conflictos_totales")
  report["estado"]="DIAGNOSTICO_OFICIAL_MENSUAL_LISTO_PENDIENTE_CARGA"
  report["conflictos_informativos"]=polic.get("conflictos_totales",0)
  report["carga_autorizada"]=False
  report["traslado_autorizado"]=False
  guardar_politica=home/"precedencia_oficial_mensual.json"
  guardar_politica.write_text(json.dumps({"periodo":period,"fuente_prioritaria":"HISTORICO_OFICIAL_MENSUAL","estado":"PRECEDENCIA_OFICIAL_DOCUMENTADA","observaciones":"Diferencias registradas; prevalece valor no vacío del histórico oficial del mismo mes; filas solo operativas y campos sin cobertura se conservan.","conflictos_detectados":polic.get("conflictos_totales",0)},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 except subprocess.CalledProcessError as exc:
  report["estado"]="BLOQUEADO"
  report["etapas"].append({"etapa":Path(exc.cmd[1]).stem if len(exc.cmd)>1 else "desconocida","resultado":"ERROR","codigo":exc.returncode})
  report["motivo"]="Etapa fallida; inspeccionar salida terminal e informes locales. No se hicieron escrituras."
  save()
  raise SystemExit(exc.returncode)
 report["fin_chile"]=dt.datetime.now(ZoneInfo("America/Santiago")).isoformat()
 save()
 print("RESUMEN:",path,report["estado"],flush=True)
if __name__=="__main__":main()
