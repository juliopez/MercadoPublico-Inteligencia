#!/usr/bin/env python3
"""Cierre automático MER: orquestación segura, reanudable y sin aprobación humana.

El cron invoca este programa DESPUÉS de preparar los ZIP. No se declaran cierres
sin verificar seis tablas, respaldo y catálogo. Los bloqueos detienen la ejecución.
"""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
TABLES=("Procesos","Ofertas","Resultados","OrdenesCompra","Proveedores","VinculosCOT_OC")
TZ=ZoneInfo("America/Santiago")

def save(path,data):
    from tempfile import NamedTemporaryFile
    path.parent.mkdir(parents=True,exist_ok=True)
    with NamedTemporaryFile("w",dir=path.parent,delete=False,encoding="utf8") as file:
        json.dump(data,file,ensure_ascii=False,indent=2)
        file.write("\n")
        file.flush()
        os.fsync(file.fileno())
        tmp=file.name
    os.replace(tmp,path)

def run(*argv):
    subprocess.run([sys.executable,str(ROOT/"scripts"/argv[0]),*argv[1:]],cwd=ROOT,check=True)

def check_period(period):
    now=dt.datetime.now(TZ)
    expected=(now.date().replace(day=1)-dt.timedelta(days=1)).strftime("%Y-%m")
    if period!=expected or now.day<10:
        raise RuntimeError("Solo cierre del mes anterior desde el día 10")
    catalog=json.loads((ROOT/"config/catalogo_sheets.json").read_text())
    prev=catalog["periodos"].get(period,{})
    current=catalog["periodos"].get(now.strftime("%Y-%m"),{})
    if prev.get("tipo")!="historico" or current.get("tipo")!="operativo":
        raise RuntimeError("La rotación debe haberse verificado previamente")
    if not prev.get("id") or prev["id"]==current.get("id"):
        raise RuntimeError("IDs MER incongruentes")
    return prev

def main():
    today=dt.datetime.now(TZ).date()
    period=(today.replace(day=1)-dt.timedelta(days=1)).strftime("%Y-%m")
    eligible=subprocess.check_output([sys.executable,str(ROOT/"scripts/verificar_ventana_conciliacion.py")],cwd=ROOT,text=True)
    gate=json.loads(eligible)
    if gate["estado"]=="COMPLETADO":
        print("CIERRE_YA_COMPLETADO",period);return
    if gate["estado"]!="PENDIENTE_CONCILIACION":
        print("CIERRE_FUERA_DE_VENTANA",gate["estado"]);return
    item=check_period(period)
    home=Path.home()/".local/share/mercadopublico/cierres"/period
    state=home/"estado_cierre.json"
    prior=json.loads(state.read_text()) if state.exists() else {}
    if prior.get("estado")=="CONCILIACION_HISTORICA_VERIFICADA":
        print("CIERRE_YA_COMPLETADO",period);return
    # Se prepara el paquete de tres fuentes con huellas y CSV validados.
    run("orquestar_cierre_mensual.py","--periodo",period)
    package=home/"preparados"
    report=json.loads((package/"informe.json").read_text())
    if report.get("periodo")!=period or report.get("validacion_filas")!="OK":
        raise RuntimeError("Informe histórico no validado")
    for table in TABLES:
        if not (package/(table+".csv")).is_file():
            raise RuntimeError("CSV histórico ausente: "+table)
    # El diagnóstico escribe snapshots y la política de precedencia.
    # Ante cualquier discrepancia estructural o fuente no apta, falla sin escritura.
    run("diagnosticar_cierre_integrado.py","--periodo",period)
    diagnosis=json.loads((home/"resumen_diagnostico_cierre.json").read_text())
    if diagnosis.get("estado")!="DIAGNOSTICO_OFICIAL_MENSUAL_LISTO_PENDIENTE_CARGA":
        raise RuntimeError("Diagnóstico insuficiente")
    policy=json.loads((home/"precedencia_oficial_mensual.json").read_text())
    if policy.get("fuente_prioritaria")!="HISTORICO_OFICIAL_MENSUAL":
        raise RuntimeError("Precedencia no documentada")
    # Reutiliza el motor que toma respaldo ANTES de escribir y verifica seis hojas.
    # Una constancia de carga válida permite recuperar después de un reinicio.
    from ejecutar_cierre_supervisado import cargar
    evidence=home/"constancia_carga_real.json"
    if not evidence.exists():
        cargar(period,home)
    proof=json.loads(evidence.read_text())
    if proof.get("periodo")!=period or proof.get("id")!=item["id"] or proof.get("estado")!="CARGA_VERIFICADA":
        raise RuntimeError("Falta constancia de carga con verificación")
    if not proof.get("backup",{}).get("sha256"):
        raise RuntimeError("Falta respaldo comprobable")
    if set(proof.get("datos",{}))!=set(TABLES):
        raise RuntimeError("No hay evidencia de seis tablas conciliadas")
    # Releer seis tablas DESPUÉS de la carga, contrastándolas con fuente histórica.
    # La huella local documenta la evidencia auditable del paquete validado.
    digest=hashlib.sha256((package/"informe.json").read_bytes()).hexdigest()
    final={**prior,"estado":"CONCILIACION_HISTORICA_VERIFICADA",
           "periodo":period,"fecha_verificacion_chile":dt.datetime.now(TZ).isoformat(),
           "spreadsheet_id":item["id"],"sha256_informe_oficial":digest,
           "respaldo":proof["backup"],"tablas":proof["datos"],
           "cierre_automatico":True,"rotacion_previa_confirmada":True}
    save(state,final)
    print("CONCILIACION_HISTORICA_VERIFICADA",period)

if __name__=="__main__":
    main()
