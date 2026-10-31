#!/usr/bin/env python3
"""Publica período histórico conciliado y confirma GitHub Pages antes de cerrar.

Independiente del cron de las 16:00. Fallos dejan estado pendiente para recuperación.
"""
import argparse,datetime as dt,json,os,subprocess,sys,time,urllib.parse,urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
TZ=ZoneInfo("America/Santiago")
ENTITIES=("procesos","ofertas","resultados","ordenescompra")
def command(*argv):
    return subprocess.check_output(argv,cwd=ROOT,text=True).strip()
def run(*argv):
    subprocess.run(argv,cwd=ROOT,check=True)
def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))
def verify(period):
    root=ROOT/"frontend-v2/data"
    cat=load(root/"catalogo-publico.json")
    entries=[x for x in cat["periodos"] if x["periodo"]==period]
    if len(entries)!=1 or entries[0].get("tipo")!="historico":
        raise ValueError("El catálogo público no contiene histórico único")
    entry=entries[0]
    for ent in ENTITIES:
        total=sum(len(load(ROOT/"frontend-v2"/p)) for p in entry["partes"][ent])
        count=entry["conteos"][ent]
        anal=load(root/"analitica"/period/(ent+".json"))
        profile=load(root/"perfiles"/period/ent/"meta.json")
        search=load(root/"busqueda"/period/ent/"meta.json")
        if total!=count or anal["registros"]!=count or profile["registros"]!=count or search["conteo"]!=count:
            raise ValueError("Desfase de índices: "+ent)
        if ent=="procesos" and sum(int(v) for _,v in anal["modalidades"])!=count:
            raise ValueError("Modalidades inconsistentes")
    return entry
def web_json(url):
    req=urllib.request.Request(url,headers={"Cache-Control":"no-cache","User-Agent":"MER-cierre-mensual/1"})
    with urllib.request.urlopen(req,timeout=35) as f:return json.load(f)
def publish(period):
    run(sys.executable,"scripts/exportar_mer_historico_conciliado_v2.py","--periodo",period,"--aplicar","--incluir-api")
    for entity in ENTITIES:
        for script in ("indexar_busqueda_frontend_v2.py","generar_perfiles_v2.py","generar_analitica_v2.py"):
            run(sys.executable,"scripts/"+script,"--periodo",period,"--entidad",entity)
    run(sys.executable,"scripts/indexar_relaciones_frontend_v2.py","--periodo",period)
    run(sys.executable,"scripts/indexar_relaciones_procesos_v2.py","--periodo",period)
    entry=verify(period)
    command("git","add","-A","--","frontend-v2/data")
    run("git","diff","--cached","--check")
    if command("git","diff","--cached","--name-only"):
        run("git","-c","user.name=MER cierre automatico","-c","user.email=cierre-local@users.noreply.github.com","commit","-m",f"data(cierre): historico oficial conciliado {period}")
        run("git","push","origin","main")
    else:
        # Asegurar una ejecucion verificable de Pages aun sin cambios de datos.
        run("gh","workflow","run","preview-frontend-v2.yml","--ref","main")
    sha=command("git","rev-parse","HEAD")
    # El push de índices dispara Pages; no despachar workflow duplicado.
    deadline=time.monotonic()+20*60
    url="https://api.github.com/repos/juliopez/MercadoPublico-Inteligencia/actions/workflows/preview-frontend-v2.yml/runs?head_sha="+sha+"&per_page=20"
    while time.monotonic()<deadline:
        runs=json.loads(command("gh","api",url)).get("workflow_runs",[])
        complete=[r for r in runs if r.get("head_sha")==sha and r.get("status")=="completed"]
        if any(r.get("conclusion")=="failure" for r in complete):
            raise RuntimeError("Pages falló para commit "+sha)
        if any(r.get("conclusion")=="success" for r in complete):
            break
        time.sleep(15)
    else:
        raise TimeoutError("Pages aún sin confirmar; reintentar solo publicación")
    base="https://juliopez.github.io/MercadoPublico-Inteligencia/frontend-v2/data/"
    expected=entry["conteos"]
    # La respuesta del sitio debe reflejar el período y cada entidad.
    for attempt in range(12):
        try:
            remote=web_json(base+"catalogo-publico.json?ver="+urllib.parse.quote(sha))
            published=next(x for x in remote["periodos"] if x["periodo"]==period)
            if published["conteos"]==expected and published.get("tipo")=="historico":
                analytics=web_json(base+"analitica/"+period+"/procesos.json?ver="+urllib.parse.quote(sha))
                if analytics["registros"]==expected["procesos"]:
                    # Cerrar el catálogo privado solo DESPUÉS de Pages verificado.
                    config_path=ROOT/"config/catalogo_sheets.json"
                    config=load(config_path)
                    record=config["periodos"][period]
                    if record.get("tipo")!="historico":
                        raise ValueError("Catálogo interno no está archivado")
                    record["estado"]="cerrado_tras_carga_oficial_verificada"
                    tmp=config_path.with_suffix(".json.tmp")
                    tmp.write_text(json.dumps(config,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
                    os.replace(tmp,config_path)
                    run("git","add","--","config/catalogo_sheets.json")
                    run("git","diff","--cached","--check")
                    if command("git","diff","--cached","--name-only"):
                        run("git","-c","user.name=MER cierre automatico","-c","user.email=cierre-local@users.noreply.github.com","commit","-m",f"chore(cierre): verificar historico oficial {period}")
                        run("git","push","origin","main")
                    print("PAGES_HISTORICO_VERIFICADO",period,sha)
                    return sha,expected
        except (OSError,KeyError,StopIteration,ValueError):
            pass
        time.sleep(10)
    raise RuntimeError("Pages no sirve aún datos consistentes para "+period)
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--periodo",required=True)
    a=p.parse_args()
    now=dt.datetime.now(TZ)
    prev=(now.date().replace(day=1)-dt.timedelta(days=1)).strftime("%Y-%m")
    if a.periodo!=prev or now.day<10:raise SystemExit("Período/fecha fuera de cierre")
    folder=Path.home()/".local/share/mercadopublico/cierres"/prev
    proof=load(folder/"constancia_carga_real.json")
    if proof.get("estado")!="CARGA_VERIFICADA" or proof.get("periodo")!=prev:
        raise SystemExit("Sin conciliación real verificada")
    sha,counts=publish(prev)
    print(json.dumps({"periodo":prev,"estado":"PUBLICACION_HISTORICA_VERIFICADA","commit":sha,"conteos":counts},ensure_ascii=False))
if __name__=="__main__":main()
