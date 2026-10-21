#!/usr/bin/env python3
"""Verificación acotada CA→OC en API oficial, sin cambiar tablas ni registrar credenciales."""
import datetime,json,os,re,sys
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
PROCESS="839-4-COT26"
CANDIDATE="839-10-AG26"
def get(url,ticket):
 req=Request(url,headers={"ticket":ticket,"Accept":"application/json","User-Agent":"Observatorio-MP-auditoria/1.0"})
 try:
  with urlopen(req,timeout=35) as response:return response.status,json.loads(response.read(4_000_000))
 except HTTPError as e:return e.code,None
 except (URLError,TimeoutError,ValueError,json.JSONDecodeError):return None,None
def main():
 ticket=os.getenv("CHILECOMPRA_TICKET","").strip()
 result={"proceso":PROCESS,"oc_candidata":CANDIDATE,"consultado_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"estado":"pendiente_verificacion","motivo":"","api_ca_http":None,"api_oc_http":None,"coincidencia_oficial":False}
 if not ticket:
  result["motivo"]="Sin credencial oficial configurada; no se consultó API"
 else:
  status,data=get("https://api2.mercadopublico.cl/v2/compra-agil/"+PROCESS,ticket)
  result["api_ca_http"]=status
  if status!=200 or not isinstance(data,dict):
   result["motivo"]="API de Compra Ágil no entregó respuesta verificable"
  else:
   payload=data.get("payload") or {}
   # Buscar código público únicamente en campos de OC, nunca en textos libres.
   candidates=[]
   for obj in [payload.get("orden_compra"),payload.get("ordenes_compra")]:
    if isinstance(obj,dict):candidates.append(obj)
    elif isinstance(obj,list):candidates.extend(v for v in obj if isinstance(v,dict))
   fields=("codigo_oc","codigo_orden_compra","codigo","numero_oc","codigoOrdenCompra")
   official_codes={str(o.get(k) or "").strip() for o in candidates for k in fields if o.get(k)}
   for k in ("codigo_oc","codigo_orden_compra"):
    if payload.get(k):official_codes.add(str(payload[k]).strip())
   result["oc_publicas_identificadas"]=sorted(x for x in official_codes if re.fullmatch(r"[0-9]+-[0-9]+-AG[0-9]{2}",x))
   if CANDIDATE in official_codes:
    result["coincidencia_oficial"]=True
    result["estado"]="referencia_oc_informada_por_api_compra_agil"
    result["motivo"]="La API del proceso incluye explícitamente código público de OC candidata"
   else:
    result["motivo"]="La API no informa el código público candidato en campos de OC; sin confirmar vínculo"
   # Segundo cotejo de código público contra API OC, sin extrapolar referencia.
   status2,oc=get("https://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json?codigo="+CANDIDATE,ticket)
   result["api_oc_http"]=status2
   if status2==200 and isinstance(oc,dict):
    rows=oc.get("Listado") or []
    matching=[item for item in rows if str(item.get("Codigo") or "").strip()==CANDIDATE]
    result["oc_publica_identificada"]=bool(matching)
    if matching and str(matching[0].get("CodigoLicitacion") or "").strip()==PROCESS:
     result["coincidencia_oficial"]=True;result["estado"]="confirmado_referencia_oc_oficial";result["motivo"]="CódigoLicitacion de OC coincide exactamente con Compra Ágil"
 result["verificacion_suficiente_para_vincular"]=result["coincidencia_oficial"]
 os.makedirs("docs/auditorias",exist_ok=True)
 path="docs/auditorias/VERIFICACION_OFICIAL_839-4-COT26_2026-10-21.json"
 with open(path,"w",encoding="utf8") as f:json.dump(result,f,ensure_ascii=False,indent=2)
 print("VERIFICACION_CA_OC",result["estado"],"CA_HTTP",result["api_ca_http"],"OC_HTTP",result["api_oc_http"])
 return 0
if __name__=="__main__":sys.exit(main())
