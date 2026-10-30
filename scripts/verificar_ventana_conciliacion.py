#!/usr/bin/env python3
"""Puerta segura de conciliación: día 10 o hábil siguiente, Chile; sin escrituras."""
import argparse,datetime as dt,json,pathlib,sys
from zoneinfo import ZoneInfo
ROOT=pathlib.Path(__file__).resolve().parents[1]
TZ=ZoneInfo("America/Santiago")
def first_eligible(today,holidays):
 first=today.replace(day=10)
 while first.weekday()>4 or first.isoformat() in holidays:first+=dt.timedelta(days=1)
 return first
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--fecha",help="AAAA-MM-DD, exclusivamente para pruebas")
 p.add_argument("--feriados",default=str(ROOT/"config/feriados_chile_conciliacion.json"))
 args=p.parse_args()
 now=dt.date.fromisoformat(args.fecha) if args.fecha else dt.datetime.now(TZ).date()
 cfg=json.loads(pathlib.Path(args.feriados).read_text())
 holiday=set(cfg.get("fechas",[]))
 if str(now.year) not in cfg.get("anios_verificados",[]):raise SystemExit("BLOQUEO: feriados del año sin verificar")
 eligible=first_eligible(now,holiday)
 prev=(now.replace(day=1)-dt.timedelta(days=1)).strftime("%Y-%m")
 if now<eligible or now.weekday()>4 or now.isoformat() in holiday:
  print(json.dumps({"estado":"NO_CORRESPONDE","fecha":now.isoformat(),"habil_desde":eligible.isoformat(),"periodo":prev}));return
 cat=json.loads((ROOT/"config/catalogo_sheets.json").read_text())
 if prev not in cat["periodos"]:raise SystemExit("BLOQUEO: mes anterior no catalogado")
 base=pathlib.Path.home()/".local/share/mercadopublico/cierres"/prev
 state=base/"estado_cierre.json"
 completed=False
 if state.exists():
  obj=json.loads(state.read_text())
  completed=obj.get("estado")=="CONCILIACION_HISTORICA_VERIFICADA"
 status="COMPLETADO" if completed else "PENDIENTE_CONCILIACION"
 print(json.dumps({"estado":status,"fecha":now.isoformat(),"habil_desde":eligible.isoformat(),"periodo":prev,"accion":"REVISAR_Y_EJECUTAR_CIERRE_SUPERVISADO" if not completed else "NINGUNA"}))
if __name__=="__main__":main()
