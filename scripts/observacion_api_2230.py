#!/usr/bin/env python3
"""Prueba nocturna acotada: una página de lista y máximo 2 detalles; no escribe MER."""
import base64,datetime as dt,hashlib,json,os,pathlib,secrets,time,urllib.error,urllib.parse,urllib.request
from zoneinfo import ZoneInfo
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes,serialization
PUBKEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAs0l2RSXGsvsS/ebuBaCG
6/3T4Ng4LpZ6OK0HYWZWY/HeOCba+cgmERKtVPGfUGJ7GjmuhRQ5Lc4M+OEojNf9
lMfbDDFaN6HvOCdGljqogwi+hb/qJP+TNJQW1A1JxEsDZvHBPhjZrue2lShYWKRr
qc31joiqh8ye055eH/MIDdg5uBDwwAaPN7+qjIiYm+oDSM10NqDLUoA+q+zv/fGD
zaNh69G1CpVgHmVBHWpR+hBCQ64UbgSEWEve0u+a+mAKj/SKHpBZtfbrhD62M2fk
YiiJblkCP0I7vXa10TJGRD7PHjZFXxsuNhdHGuSR69ij9V60glht2BSUoMgCu1ty
BwIDAQAB
-----END PUBLIC KEY-----"""
BASE="https://api2.mercadopublico.cl/v2/compra-agil"
def get(url,ticket):
 req=urllib.request.Request(url,headers={"ticket":ticket,"Accept":"application/json","User-Agent":"MER-API-observacion-2230/1"})
 with urllib.request.urlopen(req,timeout=30) as resp:
  raw=resp.read(1500001)
  if len(raw)>1500000:raise ValueError("Respuesta supera 1.5MB")
  return raw,json.loads(raw)
def main():
 now=dt.datetime.now(ZoneInfo("America/Santiago"))
 if now.hour!=22 or now.minute<25 or now.minute>55 or now.weekday()>4:
  print("SKIP: fuera de ventana 22:25-22:55 Santiago dias habiles");return
 ticket=os.environ.get("CHILECOMPRA_TICKET","").strip()
 if not ticket:raise SystemExit("BLOQUEADO: falta CHILECOMPRA_TICKET")
 # Preparación de periodo: solo octubre 2026, dos consultas de detalle máximo.
 query=urllib.parse.urlencode({"publicado_desde":"2026-10-01T00:00:00","publicado_hasta":"2026-10-01T23:59:59","tamano_pagina":"10","numero_pagina":"1"})
 out={"fecha_chile":now.isoformat(),"modo":"observacion_sin_escritura","consultas":[]}
 try:
  _,listed=get(BASE+"?"+query,ticket)
  items=(listed.get("payload") or {}).get("items") or []
  if not isinstance(items,list):raise ValueError("Listado no es lista")
  seen={"3853-565-COT26","5668-58-COT26","607603-61-COT26"}
  candidates=[]
  for it in items:
   if not isinstance(it,dict):continue
   code=str(it.get("codigo") or "").strip()
   if code.endswith("-COT26") and code not in seen and code not in candidates:candidates.append(code)
  public=serialization.load_pem_public_key(PUBKEY.encode())
  for code in candidates[:2]:
   time.sleep(3)
   try:
    raw,doc=get(BASE+"/"+urllib.parse.quote(code,safe=""),ticket)
    p=doc.get("payload") or {}
    pub=str((p.get("fechas") or {}).get("fecha_publicacion") or "")
    if p.get("codigo")!=code or not pub.startswith("2026-10"):raise ValueError("Mes/codigo no coinciden")
    aes=AESGCM.generate_key(bit_length=256);nonce=secrets.token_bytes(12)
    key=public.encrypt(aes,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
    out["consultas"].append({"codigo":code,"resultado":"OK","num_cotizaciones":len(p.get("proveedores_cotizando") or []),
       "sha256":hashlib.sha256(raw).hexdigest(),"key":base64.b64encode(key).decode(),
       "nonce":base64.b64encode(nonce).decode(),"cifrado":base64.b64encode(AESGCM(aes).encrypt(nonce,raw,code.encode())).decode()})
   except urllib.error.HTTPError as e:
    out["consultas"].append({"codigo":code,"resultado":"HTTP_"+str(e.code)})
    if e.code==429:break
   except (ValueError,urllib.error.URLError) as e:
    out["consultas"].append({"codigo":code,"resultado":type(e).__name__})
 except urllib.error.HTTPError as e:
  out["listado_error"]="HTTP_"+str(e.code)
 pathlib.Path(os.environ["RUNNER_TEMP"]).joinpath("reporte-api-2230.json").write_text(json.dumps(out,ensure_ascii=False))
 print(json.dumps({"listado_error":out.get("listado_error"),"consultas":[{"codigo":x["codigo"],"resultado":x["resultado"],"ofertas":x.get("num_cotizaciones")} for x in out["consultas"]]},ensure_ascii=False))
if __name__=="__main__":main()
