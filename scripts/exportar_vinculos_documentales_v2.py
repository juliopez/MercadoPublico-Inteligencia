#!/usr/bin/env python3
"""Exportar vínculos documentales MER al registro público V2, sin textos ni RUT.
Lee únicamente las hojas catalogadas. Rechaza conflictos de una misma OC.
"""
import argparse,datetime as dt,json,os,pathlib,re
from zoneinfo import ZoneInfo
ROOT=pathlib.Path(__file__).resolve().parents[1]
DEST=ROOT/"frontend-v2/data/vinculos-oc-verificados.json"
COT=re.compile(r"^\d{1,7}-\d{1,9}-COT\d{2,4}$",re.I)
SCHEMA=["id_vinculo","codigo_cot","codigo_oc","origen_vinculo","estado_oc_historico","fecha_aceptacion_oc","relacion_confiable"]
def main():
 p=argparse.ArgumentParser();p.add_argument("--aplicar",action="store_true");a=p.parse_args()
 import gspread
 from google.oauth2.service_account import Credentials
 secret=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
 if not secret or not pathlib.Path(secret).is_file():raise RuntimeError("Falta credencial local")
 gc=gspread.authorize(Credentials.from_service_account_file(secret,scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]))
 cat=json.loads((ROOT/"config/catalogo_sheets.json").read_text())["periodos"]
 today=dt.datetime.now(ZoneInfo("America/Santiago")).strftime("%Y-%m")
 old=json.loads(DEST.read_text())
 if not isinstance(old.get("vinculos"),list):raise ValueError("Registro público incompatible")
 links={}
 for row in old["vinculos"]:
  pair=(row["codigo_proceso"].upper(),row["codigo_oc"].upper())
  links[pair]=row
 found={}; oc_candidates={}
 for period,meta in sorted(cat.items()):
  if period>today or (period!=today and meta.get("tipo")!="historico"):continue
  if not meta.get("id"):continue
  rows=gc.open_by_key(meta["id"]).worksheet("VinculosCOT_OC").get_all_values()
  if not rows or rows[0]!=SCHEMA:raise ValueError("Cabeceras inválidas: "+period)
  for row in rows[1:]:
   row=(row+[""]*7)[:7]
   _,cot,oc,origin,_,_,certainty=row
   cot=cot.strip().upper();oc=oc.strip().upper()
   if not COT.fullmatch(cot) or not oc:continue
   # Los vínculos explícitos de ZIP COT ya pertenecen al MER pero no al
   # fichero documental de fichas. No declarar como documental la totalidad.
   if certainty not in ("REFERENCIA_DOCUMENTAL_OC","DOCUMENTO_OFICIAL_VALIDADO") and not origin.startswith("OC:"):continue
   pair=(cot,oc)
   entry={"codigo_proceso":cot,"codigo_oc":oc,"periodo_oc":period,
          "estado_verificacion":"confirmado_documentalmente",
          "fuente":"MER v2 / ZIP oficial OC / Descripcion/Obervaciones",
          "limite":"Relación de origen; no acredita adjudicación ni pago"}
   found[pair]=entry
   oc_candidates.setdefault(oc,set()).add(cot)
 ambiguous={oc for oc,cots in oc_candidates.items() if len(cots)>1}
 added=0
 for pair,entry in sorted(found.items()):
  if pair[1] in ambiguous or pair in links:continue
  links[pair]=entry;added+=1
 merged=sorted(links.values(),key=lambda r:(r.get("periodo_oc",""),r["codigo_proceso"],r["codigo_oc"]))
 result={"modo":"APLICAR" if a.aplicar else "SIMULACION","documentales_mer":len(found),"nuevos":added,"oc_ambiguas":len(ambiguous),"total_publico":len(merged)}
 print(json.dumps(result,ensure_ascii=False))
 if not a.aplicar:return
 if added==0:return
 out=dict(old);out["actualizado"]=today;out["vinculos"]=merged
 tmp=DEST.with_suffix(".json.tmp");tmp.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
 os.replace(tmp,DEST)
 print("VINCULOS_PUBLICOS_GENERADOS",len(merged))
if __name__=="__main__":main()
