#!/usr/bin/env python3
"""Completa SOLO presupuestos CLP visibles faltantes en Procesos del MER operativo.
Predeterminado: simulacion sin escrituras. No modifica ZIP, historicos ni otras columnas.
"""
import argparse,csv,datetime as dt,io,json,os,pathlib,urllib.request,zipfile,collections,hashlib,time
from decimal import Decimal,InvalidOperation
from zoneinfo import ZoneInfo
ROOT=pathlib.Path(__file__).resolve().parents[1]
def monto(row):
 if (row.get("CodigoMoneda") or "").strip().upper()!="CLP":return None
 if (row.get("Estimacion") or "").strip()!="1":return None
 if (row.get("VisibilidadMonto") or "").strip()!="1":return None
 raw=(row.get("MontoEstimado") or "").strip().replace(" ","")
 try:
  number=Decimal(raw)
  if number.is_finite() and number>0 and number==number.to_integral_value() and number<Decimal("1000000000000000"):return str(number.quantize(Decimal("1")))
 except InvalidOperation:pass
 return None
def source(url):
 import tempfile,shutil
 values=collections.defaultdict(set);counts=collections.Counter()
 with tempfile.TemporaryDirectory(prefix="montos_mer_reparacion_") as temp:
  path=pathlib.Path(temp)/"lic.zip"
  with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"MER-auditoria-montos/1.0"}),timeout=180) as inp,path.open("wb") as out:shutil.copyfileobj(inp,out)
  with zipfile.ZipFile(path) as z:
   assert z.testzip() is None,"ZIP CRC falló"
   for file in z.infolist():
    if not file.filename.lower().endswith(".csv"):continue
    with z.open(file) as raw:
     reader=csv.DictReader(io.TextIOWrapper(raw,encoding="latin-1",newline=""),delimiter=";")
     assert {"CodigoExterno","MontoEstimado","CodigoMoneda","Estimacion","VisibilidadMonto"}.issubset(set(reader.fieldnames or [])),"Cabeceras oficiales no compatibles"
     for row in reader:
      key=((row.get("CodigoExterno") or row.get("Codigo") or "").strip().upper())
      if not key:continue
      counts["filas"]+=1
      val=monto(row)
      if val:values[key].add(val);counts["filas_presupuesto_visible_clp"]+=1
 return values,counts
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--aplicar",action="store_true")
 p.add_argument("--periodo",default="2026-10")
 a=p.parse_args()
 if a.periodo!=dt.datetime.now(ZoneInfo("America/Santiago")).strftime("%Y-%m"):p.error("Solo período operativo vigente")
 import gspread
 from google.oauth2.service_account import Credentials
 from importlib.util import spec_from_file_location,module_from_spec
 cred=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
 if not cred or not pathlib.Path(cred).is_file():p.error("Credencial Ubuntu requerida")
 src=json.loads((ROOT/"config/fuentes_descarga_mensual.json").read_text())["fuentes"]["licitaciones"]
 year,month=a.periodo.split("-")
 source_url=src.format(yyyy=year,mm=month)
 candidates,counts=source(source_url)
 conflict={k for k,v in candidates.items() if len(v)!=1}
 scope=["https://www.googleapis.com/auth/spreadsheets"] if a.aplicar else ["https://www.googleapis.com/auth/spreadsheets.readonly"]
 auth=gspread.authorize(Credentials.from_service_account_file(cred,scopes=scope))
 cfg=json.loads((ROOT/"config/catalogo_sheets.json").read_text())
 ws=auth.open_by_key(cfg["periodos"][a.periodo]["id"]).worksheet("Procesos")
 values=ws.get_all_values()
 spec=spec_from_file_location("mer_schema",ROOT/"scripts/importador_historicos_v2.py")
 module=module_from_spec(spec);spec.loader.exec_module(module)
 expected=module.SCHEMA["Procesos"]
 assert values and values[0]==expected,"Cabeceras MER inesperadas"
 codecol=expected.index("codigo");amountcol=expected.index("monto_disponible_clp")
 def colname(n):
  s=""
  while n:n,rem=divmod(n-1,26);s=chr(65+rem)+s
  return s
 cell=colname(amountcol+1)
 changes=[];seen=set();skipped=collections.Counter()
 for i,row in enumerate(values[1:],start=2):
  code=(row[codecol] if len(row)>codecol else "").strip().upper()
  if code in seen:raise ValueError("PK duplicada en MER: "+code)
  seen.add(code)
  existing=(row[amountcol] if len(row)>amountcol else "").strip()
  if existing:skipped["importe_existente"]+=1;continue
  if code in conflict:skipped["fuente_ambigua"]+=1;continue
  amounts=candidates.get(code)
  if amounts and len(amounts)==1:changes.append((f"{cell}{i}",next(iter(amounts))))
  else:skipped["sin_presupuesto_CLP_visible"]+=1
 report={"periodo":a.periodo,"modo":"APLICAR" if a.aplicar else "SIMULACION","filas_sheet":len(values)-1,
         "celdas_a_completar":len(changes),"celdas_existentes_preservadas":skipped["importe_existente"],
         "ambiguedades_fuente":len(conflict),"motivos_sin_cambio":dict(skipped),"filas_fuente":dict(counts)}
 print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
 if not a.aplicar:return
 if not changes:print("SIN_CAMBIOS");return
 backup=ROOT/"salida_operativa"/("respaldo_montos_procesos_"+a.periodo+"_"+dt.datetime.now().strftime("%Y%m%d_%H%M%S")+".csv")
 backup.parent.mkdir(parents=True,exist_ok=True)
 with backup.open("w",newline="",encoding="utf-8") as file:csv.writer(file).writerows(values)
 print("RESPALDO_LOCAL",backup,flush=True)
 for start in range(0,len(changes),60):
  updates=[{"range":ref,"values":[[val]]} for ref,val in changes[start:start+60]]
  ws.batch_update(updates,value_input_option="RAW")
  time.sleep(1)
 check=ws.get_all_values()
 for ref,value in changes:
  n=int("".join(ch for ch in ref if ch.isdigit()))
  assert check[n-1][amountcol]==value,("Fallo verificación",ref)
 print("MONTOS_OPERATIVOS_COMPLETADOS_Y_VERIFICADOS",len(changes))
if __name__=="__main__":main()
