"""Simulación de estados de evidencia COT–OC, agosto 2026. Nunca escribe a Google Sheets."""
import csv,json,collections,os
from datetime import datetime,timezone
D=os.getcwd()
def read(name):
    with open(os.path.join(D,name),encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
links=read("auditoria_cot_oc_corregida_2026_08_detalle.csv")
conc=read("conciliacion_COT_OC_agosto_2026_procesos.csv")
ruts=read("auditoria_rut_cot_vs_sucursal_oc_agosto.csv")
verified={(x["codigo_cot"],x["codigo_oc"]) for x in ruts if x["rut_cot_coincide_sucursal_oc"]=="SI"}
assert len(links)==68093 and len(conc)==65945 and len(verified)==8586
good={"Aceptada","Recepción conforme"}
levels=["OC_ACEPTADA_MONTO_COINCIDE","OC_ACEPTADA_RUT_COINCIDE_NOMBRE_DIFIERE",
        "OC_ACEPTADA_MONTO_DIFIERE","OC_ACEPTADA_FUERA_CORTE","SIN_OC_ACEPTADA"]
by=collections.defaultdict(list)
for r in links:by[r["codigo_cot"]].append(r)
assert set(by)=={r["codigo_cot"] for r in conc}
out=[]
for x in conc:
    cot=x["codigo_cot"]; candidates=[]
    for r in by[cot]:
        if r["estado_oc_desde_cot"] not in good:continue
        cat=r["categoria"]
        if cat=="CODIGO_OC_PROVEEDOR_MONTO_COINCIDEN":level=levels[0]
        elif cat=="CODIGO_OC_COINCIDE_PROVEEDOR_DISTINTO" and (cot,r["codigo_oc"]) in verified:level=levels[1]
        elif cat=="CODIGO_OC_PROVEEDOR_COINCIDEN_MONTO_DIFERENTE":level=levels[2]
        elif cat=="OC_NO_PRESENTE_EN_HISTORICO_AGOSTO":level=levels[3]
        else:raise ValueError("Coincidencia sin clasificar: "+str(r))
        candidates.append((levels.index(level),level,r["codigo_oc"],r["estado_oc_desde_cot"]))
    best=min(candidates) if candidates else (4,levels[4],"","")
    out.append(dict(codigo=cot,estado_verificacion_oc_propuesto=best[1],
      oc_referencia=best[2],estado_oc_referencia=best[3],
      oc_vinculadas=len(by[cot]),oc_aceptadas_o_recepcion=sum(r["estado_oc_desde_cot"] in good for r in by[cot]),
      requiere_revision_manual="SI" if best[0]>=2 else "NO",
      validado_actual="Pendiente: selección histórica, no adjudicación verificada",
      validado_propuesto="SIN_CAMBIOS",accion_sobre_montos="NINGUNA",
      observacion="Clasificación documental provisional; no acredita adjudicación formal"))
counts=dict(collections.Counter(r["estado_verificacion_oc_propuesto"] for r in out))
assert sum(counts.values())==65945
with open("simulacion_actualizacion_resultados_agosto_2026.csv","w",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f,fieldnames=out[0]);w.writeheader();w.writerows(out)
summary={"fecha_utc":datetime.now(timezone.utc).isoformat(),"procesos":len(out),"vinculos":len(links),
         "distribucion_estados_propuestos":counts,"modificaciones_google_sheets":0,
         "advertencia":"Simulación: no modificar validado, adjudicación ni montos."}
with open("simulacion_actualizacion_resultados_agosto_2026_resumen.json","w",encoding="utf-8") as f:
    json.dump(summary,f,ensure_ascii=False,indent=2)
print(json.dumps(summary,ensure_ascii=False,indent=2))
