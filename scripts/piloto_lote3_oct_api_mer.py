#!/usr/bin/env python3
"""Captura cifrada de tres candidatos vinculados a OC de octubre; sin publicación pública."""
import os,json,time,base64,pathlib,hashlib,secrets,urllib.request,urllib.error
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization,hashes
CODES=["813-471-COT26","1699-101-COT26","538598-574-COT26"]
PUBLIC_KEY="-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAs0l2RSXGsvsS/ebuBaCG\n6/3T4Ng4LpZ6OK0HYWZWY/HeOCba+cgmERKtVPGfUGJ7GjmuhRQ5Lc4M+OEojNf9\nlMfbDDFaN6HvOCdGljqogwi+hb/qJP+TNJQW1A1JxEsDZvHBPhjZrue2lShYWKRr\nqc31joiqh8ye055eH/MIDdg5uBDwwAaPN7+qjIiYm+oDSM10NqDLUoA+q+zv/fGD\nzaNh69G1CpVgHmVBHWpR+hBCQ64UbgSEWEve0u+a+mAKj/SKHpBZtfbrhD62M2fk\nYiiJblkCP0I7vXa10TJGRD7PHjZFXxsuNhdHGuSR69ij9V60glht2BSUoMgCu1ty\nBwIDAQAB\n-----END PUBLIC KEY-----"
def main():
 ticket=os.environ.get("CHILECOMPRA_TICKET","").strip()
 if not ticket:raise SystemExit("BLOQUEO: sin ticket")
 dest=pathlib.Path(os.environ["RUNNER_TEMP"])/"capturas_octubre_cifradas.json"
 key=serialization.load_pem_public_key(PUBLIC_KEY.encode())
 out={"version":1,"candidatos":CODES,"registros":[]}
 for i,code in enumerate(CODES):
  request=urllib.request.Request("https://api2.mercadopublico.cl/v2/compra-agil/"+code,
          headers={"ticket":ticket,"Accept":"application/json","User-Agent":"MER-Piloto-Octubre-lote3"})
  try:
   with urllib.request.urlopen(request,timeout=45) as rsp:
    if rsp.status!=200:raise ValueError("HTTP inesperado")
    raw=rsp.read(8000001)
    if len(raw)>8000000:raise ValueError("Excede límite")
   doc=json.loads(raw)
   if doc.get("payload",{}).get("codigo")!=code:raise ValueError("Código no coincide")
   nonce=secrets.token_bytes(12);aes=AESGCM.generate_key(bit_length=256)
   encrypted=AESGCM(aes).encrypt(nonce,raw,code.encode())
   sealed=key.encrypt(aes,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
   out["registros"].append({"codigo":code,"estado":"ok","sha256":hashlib.sha256(raw).hexdigest(),
      "nonce":base64.b64encode(nonce).decode(),"key":base64.b64encode(sealed).decode(),
      "ciphertext":base64.b64encode(encrypted).decode()})
   print(json.dumps({"codigo":code,"estado":"respuesta_cifrada","n_cotizaciones":len(doc.get("payload",{}).get("proveedores_cotizando") or [])}))
  except (urllib.error.HTTPError,urllib.error.URLError,ValueError,KeyError,json.JSONDecodeError) as exc:
   out["registros"].append({"codigo":code,"estado":"error","clase":type(exc).__name__})
   print(json.dumps({"codigo":code,"estado":"error","tipo":type(exc).__name__}))
  if i<len(CODES)-1:time.sleep(2)
 dest.write_text(json.dumps(out,ensure_ascii=False))
if __name__=="__main__":main()
