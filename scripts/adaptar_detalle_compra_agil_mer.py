"""Adaptador puro de respuesta Compra Ágil V2 a cabeceras reales MER.
Sin HTTP, sin Sheets; no infiere moneda, adjudicación ni identidad canónica.
"""
import json,sys
OFERTAS=("id_cotizacion","codigo","id_proveedor","proveedor","monto_ofertado_clp","fecha_oferta","fuente","seleccionado","rut_proveedor_cot")
RESULTADOS=("codigo","id_cotizacion_ganadora","adjudicatario","monto_adjudicado_clp","fecha_resultado","motivo_seleccion","fuente","validado","monto_oferta_seleccionada_clp","estado_verificacion_oc")
FUENTE="API ChileCompra V2 - detalle Compra Ágil"
def txt(v): return "" if v is None else str(v)
def fila(d,cols): return {k:txt(d.get(k)) for k in cols}
def adaptar_detalle(data,*,clp_verificado=False):
    if not isinstance(data,dict) or data.get("success") not in (True,"OK"): raise ValueError("Respuesta API sin éxito")
    p=data.get("payload")
    if not isinstance(p,dict): raise ValueError("Payload inválido")
    codigo=txt(p.get("codigo")).strip()
    if "-COT" not in codigo: raise ValueError("Código Compra Ágil inválido")
    items=p.get("proveedores_cotizando")
    if not isinstance(items,list): raise ValueError("No consta lista de cotizaciones")
    ofertas=[]; seleccionadas=[]; ids=set()
    for x in items:
        if not isinstance(x,dict): raise ValueError("Oferta inválida")
        cid=txt(x.get("id_cotizacion")).strip()
        if not cid or cid in ids: raise ValueError("ID cotización vacío o duplicado")
        ids.add(cid)
        elegido=x.get("proveedor_seleccionado") in (True,1,"1")
        o=fila(dict(id_cotizacion=cid,codigo=codigo,id_proveedor=x.get("codigo_empresa"),
          proveedor=x.get("razon_social"),monto_ofertado_clp=x.get("monto_total") if clp_verificado else "",
          fecha_oferta=x.get("fecha_creacion"),fuente=FUENTE,seleccionado="1" if elegido else "0",
          rut_proveedor_cot=x.get("rut_proveedor")),OFERTAS)
        ofertas.append(o)
        if elegido: seleccionadas.append(o)
    if len(seleccionadas)>1: raise ValueError("Selección múltiple ambigua")
    resultados=[]
    if seleccionadas:
        s=seleccionadas[0]
        motivos=p.get("motivos") or {}
        if not isinstance(motivos,dict): motivos={}
        resultados=[fila(dict(codigo=codigo,id_cotizacion_ganadora=s["id_cotizacion"],
          adjudicatario="",monto_adjudicado_clp="",fecha_resultado="",
          motivo_seleccion=motivos.get("motivo_seleccion"),fuente=FUENTE,
          validado="No: selección API; adjudicación no verificada",
          monto_oferta_seleccionada_clp=s["monto_ofertado_clp"],
          estado_verificacion_oc="Pendiente de verificar OC pública"),RESULTADOS)]
    return {"codigo":codigo,"ofertas":ofertas,"resultados":resultados,
            "control":{"ofertas_api":len(ofertas),"seleccionadas_api":len(seleccionadas),
                       "montos_clp_verificados":clp_verificado,
                       "id_proveedor_pendiente":len(ofertas)}}
if __name__=="__main__":
    print(json.dumps(adaptar_detalle(json.load(sys.stdin),clp_verificado="--clp-verificado" in sys.argv),ensure_ascii=False,indent=2))
