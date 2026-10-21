#!/usr/bin/env python3
"""Descarga y simula actualización de SOLO el mes operativo MER v2.
No escribe Google Sheets, no modifica históricos ni publica frontend.
Requiere Python >=3.9; autenticación gspread opcional para comparar con Sheets.
"""
import argparse, calendar, csv, datetime as dt, hashlib, json, os, subprocess, sys, tempfile, urllib.request, urllib.error, zipfile
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
TABLES=("Procesos","Proveedores","Ofertas","OrdenesCompra","VinculosCOT_OC","Resultados")
CHILE=ZoneInfo("America/Santiago")
def periodo_actual(now=None):
    return (now or dt.datetime.now(CHILE)).strftime("%Y-%m")
def digest(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()
def url_mes(template,period):
    yyyy,mm=period.split("-")
    return template.format(yyyy=yyyy,mm=mm)
def descargar(url,path):
    req=urllib.request.Request(url,headers={"User-Agent":"MER-v2-monthly-downloader/1.0"})
    with urllib.request.urlopen(req,timeout=120) as res, path.open("wb") as out:
        import shutil
        shutil.copyfileobj(res,out,length=1024*1024)
    if path.stat().st_size==0 or not zipfile.is_zipfile(path):
        raise ValueError("Respuesta vacía o no ZIP: "+url)
    with zipfile.ZipFile(path) as z:
        names=[x for x in z.infolist() if x.filename.lower().endswith(".csv") and not x.is_dir()]
        if not names:raise ValueError("ZIP sin CSV: "+url)
        for item in z.infolist():
            if item.flag_bits & 1:raise ValueError("ZIP cifrado no admitido")
            if item.CRC is None:raise ValueError("ZIP sin CRC")
        # testzip valida CRC de contenido comprimido; indispensable antes del ETL
        corrupt=z.testzip()
        if corrupt:raise ValueError("CRC inválido: "+corrupt)
        return {"bytes":path.stat().st_size,"sha256":digest(path),"csv":len(names)}
def rows_csv(path):
    with open(path,encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        if not reader.fieldnames or reader.fieldnames[0] not in ("codigo","id_proveedor","id_cotizacion","codigo_oc","id_vinculo"):
            raise ValueError("Cabecera inesperada "+str(path))
        for row in reader:
            if None in row or None in row.values():raise ValueError("Fila mal formada "+str(path))
            yield row
def huella(row):
    return hashlib.sha256(json.dumps(row,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode("utf8")).hexdigest()
def diff_tabla(path,pk,destino,cols):
    encontrados=set();new=changed=same=0;inestables=0
    for r in rows_csv(path):
        key=r[pk].strip()
        if not key or key in encontrados:raise ValueError("Clave vacía/duplicada en "+str(path))
        encontrados.add(key)
        old=destino.get(key)
        if old is None:new+=1
        elif huella(r)==huella(old):same+=1
        else:changed+=1
    return {"nuevos":new,"modificados":changed,"sin_cambios":same,
            "en_destino_no_presentes_en_corte":len(set(destino)-encontrados)}
def comparar_sheets(folder,period,cat):
    try:import gspread;from google.auth import default
    except ImportError:raise RuntimeError("Para comparar Sheets instalar gspread y google-auth")
    import google.auth
    creds,_=google.auth.default(scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"])
    gc=gspread.authorize(creds);sheet=gc.open_by_key(cat["periodos"][period]["id"])
    if cat["periodos"][period]["tipo"]!="operativo":raise ValueError("Bloqueado: destino histórico")
    result={}
    for table in TABLES:
        src=folder/(table+".csv")
        with src.open(encoding="utf-8-sig",newline="") as f:headers=next(csv.reader(f))
        ws=sheet.worksheet(table)
        existing=ws.get_all_values()
        if existing[0]!=headers:raise ValueError("Contrato MER distinto en "+table)
        pk=headers[0];old={}
        for row in existing[1:]:
            if not row or not row[0]:continue
            row=(row+[""]*len(headers))[:len(headers)]
            if row[0] in old:raise ValueError("Duplicados en Sheet "+table)
            old[row[0]]=dict(zip(headers,row))
        result[table]=diff_tabla(src,pk,old,headers)
    return result
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--periodo",help="Solo YYYY-MM vigente en Santiago; predeterminado mes actual")
    ap.add_argument("--salida",default="salida_operativa")
    ap.add_argument("--comparar-sheets",action="store_true",help="Lectura solamente")
    ap.add_argument("--solo-local",action="store_true",help="No leer Sheets; validar fuentes y ETL")
    args=ap.parse_args()
    vigente=periodo_actual()
    period=args.periodo or vigente
    if period!=vigente:ap.error("Bloqueo: el período solicitado "+period+" no coincide con mes vigente "+vigente)
    config=json.loads((ROOT/"config/fuentes_descarga_mensual.json").read_text())
    cat=json.loads((ROOT/"config/catalogo_sheets.json").read_text())
    destino=cat["periodos"].get(period)
    if not destino or destino["tipo"]!="operativo":ap.error("No existe destino operativo registrado para "+period)
    if args.comparar_sheets and args.solo_local:ap.error("Elegir un modo de comparación")
    out=Path(args.salida).resolve()
    out.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="mer_mes_") as tmp:
        t=Path(tmp);sources={}
        for k,template in config["fuentes"].items():
            url=url_mes(template,period);# Preservar nombres compatibles con el importador histórico.
            p=t/(("COT_" if k=="compra_agil" else "")+period+".zip" if k!="ordenes_compra" else period+" (OC).zip")
            print("Descargando",k,url,flush=True)
            sources[k]=dict(url=url,archivo=p.name,**descargar(url,p))
        dest=out/("preparado_"+period)
        cmd=[sys.executable,str(ROOT/"scripts/importador_historicos_v2.py"),
             "--anio",period[:4],"--mes",str(int(period[5:])),"--licitaciones",str(t/sources["licitaciones"]["archivo"]),
             "--cot",str(t/sources["compra_agil"]["archivo"]),
             "--oc",str(t/sources["ordenes_compra"]["archivo"]),"--out",str(dest)]
        # nombres temporales deben conservar los patrones de período
        subprocess.run(cmd,check=True)
        manifest=json.loads((dest/"informe.json").read_text(encoding="utf8"))
        if manifest.get("estado")!="PREPARADO_SOLO_LECTURA_SIN_CARGA_SHEETS":raise ValueError("Preparación incompleta")
        summary={"periodo":period,"ejecutado_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
                 "destino_sheets":destino["id"],"fuentes":sources,
                 "totales_preparados":{k:manifest[k] for k in TABLES},
                 "modo":"SIMULACION_SIN_ESCRITURAS"}
        if args.comparar_sheets:summary["comparacion"]=comparar_sheets(dest,period,cat)
        (out/("simulacion_"+period+".json")).write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf8")
        print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
