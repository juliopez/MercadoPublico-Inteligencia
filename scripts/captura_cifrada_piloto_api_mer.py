#!/usr/bin/env python3
"""Única captura controlada. Publica solo JSON cifrado y resumen sin identificadores personales."""
import base64,hashlib,json,os,pathlib,secrets,urllib.request
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

CODE="839-4-COT26"
PUBLIC_KEY="""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu94Wom+ujzMvHE/Il6K5
0nDy+z2W8kRisl4fYeywRFPrnNWP7zDV2bmRkkixrMGNWhfkP5QqPcRl9bpWiU4l
8xnXPH5gws9EKyNlaGwLXMhktEyV84/2fz+mWCIC4lveuvxSiEwxZ7ipyvpZ5KJm
mSAIV76BHhmxSOnSFU938kAL1WIVxCMF/+VeSgvmosZu6K4muzSBgtoKX1L2PTR1
QpTkwKOX90l7+ka03Q8xWJts7YX35VLEwVyQWVQflKEerbllLcPW8xHLo4UQCIsY
GglM1cWGDmhkHrAfJcctxSDdZud1cQ1plpwCNjwZkBUCLLqLKLfcf12jZt3GkSMe
XwIDAQAB
-----END PUBLIC KEY-----"""
def main():
 ticket=os.environ.get("CHILECOMPRA_TICKET","").strip()
 if not ticket:raise SystemExit("BLOQUEADO: CHILECOMPRA_TICKET no disponible; no se consultó API")
 request=urllib.request.Request("https://api2.mercadopublico.cl/v2/compra-agil/"+CODE,
  headers={"ticket":ticket,"Accept":"application/json","User-Agent":"MER-Fase2-one-shot"})
 with urllib.request.urlopen(request,timeout=40) as response:
  if response.status!=200:raise RuntimeError("Respuesta no exitosa")
  raw=response.read(8_000_001)
  if len(raw)>8_000_000:raise RuntimeError("Respuesta excede límite")
 data=json.loads(raw)
 if not isinstance(data,dict) or not isinstance(data.get("payload"),dict):
  raise RuntimeError("Respuesta inesperada")
 if str(data["payload"].get("codigo"))!=CODE:raise RuntimeError("Código distinto al solicitado")
 offers=data["payload"].get("proveedores_cotizando")
 if not isinstance(offers,list):raise RuntimeError("Contenedor de ofertas ausente")
 public=serialization.load_pem_public_key(PUBLIC_KEY.encode())
 key=AESGCM.generate_key(bit_length=256);nonce=secrets.token_bytes(12)
 encrypted=AESGCM(key).encrypt(nonce,raw,CODE.encode())
 wrapped=public.encrypt(key,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
 envelope={"version":1,"codigo":CODE,"alg":"AES-256-GCM+RSA-OAEP-SHA256",
  "nonce":base64.b64encode(nonce).decode(),"key":base64.b64encode(wrapped).decode(),
  "ciphertext":base64.b64encode(encrypted).decode(),"sha256_raw":hashlib.sha256(raw).hexdigest()}
 dest=pathlib.Path(os.environ["RUNNER_TEMP"])/"mer_captura_cifrada.json"
 dest.write_text(json.dumps(envelope))
 print(json.dumps({"estado":"CAPTURA_CIFRADA","codigo":CODE,"ofertas":len(offers),
  "seleccionadas":sum(x.get("proveedor_seleccionado") in (True,1,"1") for x in offers if isinstance(x,dict)),
  "success_field":str(data.get("success")),"sha256_raw":envelope["sha256_raw"]}))
if __name__=="__main__":main()
