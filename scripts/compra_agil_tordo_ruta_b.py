#!/usr/bin/env python3
"""Ruta B Tordo: extracción aislada; jamás escribe Google Sheets ni MER."""
import argparse,csv,datetime as dt,json,pathlib,re,sqlite3,sys,time,urllib.request,urllib.parse
from zoneinfo import ZoneInfo
TZ=ZoneInfo("America/Santiago")
BASE="https://api.tordo.cl/api/v1/tenders/"
COLUMNS=["codigo","nombre","estado","convocatoria","fecha_publicacion","fecha_cierre","monto_disponible_clp","organismo_comprador","region","total_ofertas_recibidas","motivo_seleccion","url_detalle","fecha_sincronizacion","categoria","subcategoria","modalidad"]
def date(s):
    if not s:return ""
    d=dt.datetime.fromisoformat(str(s).replace("Z","+00:00"))
    return d.replace(tzinfo=TZ).astimezone(TZ).date().isoformat() if d.tzinfo is None else d.astimezone(TZ).date().isoformat()
def fetch(params):
    url=BASE+"?"+urllib.parse.urlencode(params)
    for n in range(3):
        try:
            req=urllib.request.Request(url,headers={"Accept":"application/json","User-Agent":"Observatorio-MER-Tordo-Piloto/1.0"})
            with urllib.request.urlopen(req,timeout=45) as response:
                data=response.read(8000001)
                if len(data)>8000000:raise ValueError("Respuesta excesiva")
                return json.loads(data)
        except Exception:
            if n==2:raise
            time.sleep(3*(n+1))
def row(x,now):
    code=str(x.get("codigo_externo") or "").strip().upper()
    if not re.fullmatch(r"[A-Z0-9-]+-COT[0-9]{2}",code):raise ValueError("Código inválido "+code)
    return dict(zip(COLUMNS,[code,str(x.get("nombre") or ""),str(x.get("estado") or ""),"",date(x["fecha_publicacion"]),date(x.get("fecha_cierre")),str(x.get("monto_estimado") or ""),str(x.get("nombre_organismo") or ""),str(x.get("region") or ""),"","","https://buscador.mercadopublico.cl/ficha?code="+code,now,"Compra Ágil","","Compra Ágil"]))
def run(a):
    now=dt.datetime.now(TZ)
    if dt.date.fromisoformat(a.fecha)>now.date():raise ValueError("Fecha futura")
    out=pathlib.Path(a.salida);out.mkdir(parents=True,exist_ok=True)
    found={};prev=None;ordered=True;scanned=0;pages=0;complete=False;errors=[];total=None
    for offset in range(0,a.max_paginas*100,100):
        data=fetch({"tipo_convocatoria":"compra_agil","sort_by":"fecha_publicacion","sort_order":"desc","limit":100,"offset":offset})
        items=data.get("items")
        if not isinstance(items,list) or not isinstance(data.get("total"),int):raise ValueError("Contrato incompatible")
        total=data["total"];pages+=1;scanned+=len(items)
        older=False
        for x in items:
            try:
                if x.get("tipo_convocatoria")!="compra_agil":raise ValueError("Modalidad inválida")
                day=date(x["fecha_publicacion"])
                if prev and day>prev:ordered=False
                prev=day
                if day<a.fecha:older=True
                if day==a.fecha:
                    r=row(x,now.isoformat());found[r["codigo"]]=(x,r)
            except (ValueError,TypeError,KeyError) as e:errors.append(str(e))
        if older or len(items)<100:complete=True;break
        time.sleep(a.pausa)
    latest_data=fetch({"tipo_convocatoria":"compra_agil","sort_by":"fecha_publicacion","sort_order":"desc","limit":1})
    latest=date((latest_data.get("items") or [{}])[0].get("fecha_publicacion"))
    lag=(now.date()-dt.date.fromisoformat(latest)).days if latest else None
    ok=complete and ordered and not errors and bool(found) and lag is not None and lag<=a.max_atraso_dias
    status="OK_CANDIDATO" if ok else "REVISAR_NO_APTO"
    report={"fecha":a.fecha,"instante_chile":now.isoformat(),"fuente":BASE,"procesos_unicos_dia":len(found),"registros_examinados":scanned,"paginas_leidas":pages,"total_catalogo_reportado":total,"ultima_fecha_publicacion":latest,"atraso_dias":lag,"barrido_completo":complete,"orden_correcto":ordered,"errores":errors[:30],"estado":status,"escritura_mer":False,"cobertura_oficial_demostrada":False}
    (out/("tordo_"+a.fecha+"_reporte.json")).write_text(json.dumps(report,ensure_ascii=False,indent=2))
    if complete and ordered and not errors:
        db=sqlite3.connect(out/"tordo_staging.sqlite")
        db.execute("CREATE TABLE IF NOT EXISTS procesos(codigo TEXT PRIMARY KEY,fecha TEXT,payload TEXT,mer TEXT,ultima_lectura TEXT)")
        for code,(x,r) in found.items():
            db.execute("INSERT OR REPLACE INTO procesos VALUES(?,?,?,?,?)",(code,a.fecha,json.dumps(x,ensure_ascii=False),json.dumps(r,ensure_ascii=False),now.isoformat()))
        db.commit();db.close()
        with (out/("tordo_"+a.fecha+"_procesos_preliminar.csv")).open("w",encoding="utf-8-sig",newline="") as f:
            w=csv.DictWriter(f,fieldnames=COLUMNS);w.writeheader();w.writerows(r for x,r in sorted(found.values(),key=lambda t:t[1]["codigo"]))
        (out/("tordo_"+a.fecha+"_origen.json")).write_text(json.dumps([x for x,r in found.values()],ensure_ascii=False,indent=2))
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0 if ok else 2
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--fecha",default=dt.datetime.now(TZ).date().isoformat());p.add_argument("--salida",default="salidas/tordo");p.add_argument("--max-paginas",type=int,default=300);p.add_argument("--pausa",type=float,default=1.2);p.add_argument("--max-atraso-dias",type=int,default=1)
    a=p.parse_args()
    try:
        if a.max_paginas<1 or a.pausa<1 or a.max_atraso_dias<0:raise ValueError("Parámetros inválidos")
        sys.exit(run(a))
    except Exception as e:
        print(json.dumps({"estado":"ERROR","detalle":str(e),"escritura_mer":False}),file=sys.stderr);sys.exit(1)
