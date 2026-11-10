#!/usr/bin/env python3
"""Una página de listado de CA publicadas el 27/10; cifrar íntegra respuesta."""
import os,json,base64,pathlib,urllib.parse,urllib.request,secrets,hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import serialization,hashes
from cryptography.hazmat.primitives.asymmetric import padding
from piloto_lote3_oct_api_mer import PUBLIC_KEY
def main():
 token=os.environ.get("CHILECOMPRA_TICKET","")
 if not token:raise SystemExit("Falta secreto")
 query={"publicado_desde":"2026-10-27T00:00:00","publicado_hasta":"2026-10-27T23:59:59",
        "tamano_pagina":"10","numero_pagina":"1","ordenar_por":"FechaPublicacion"}
 url="https://api2.mercadopublico.cl/v2/compra-agil?"+urllib.parse.urlencode(query)
 req=urllib.request.Request(url,headers={"ticket":token,"Accept":"application/json"})
 with urllib.request.urlopen(req,timeout=40) as r:
  raw=r.read(2000001)
  if len(raw)>2000000:raise ValueError("Excede limite")
 doc=json.loads(raw);p=doc.get("payload") or {}
 print(json.dumps({"success":str(doc.get("success")),"payload_keys":list(p.keys()) if isinstance(p,dict) else [],
                   "paginacion":p.get("paginacion") if isinstance(p,dict) else None},ensure_ascii=False))
 pub=serialization.load_pem_public_key(PUBLIC_KEY.encode());aes=AESGCM.generate_key(bit_length=256);nonce=secrets.token_bytes(12)
 obj={"nonce":base64.b64encode(nonce).decode(),"key":base64.b64encode(pub.encrypt(aes,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None))).decode(),"ciphertext":base64.b64encode(AESGCM(aes).encrypt(nonce,raw,b"listado20261027")).decode(),"sha256":hashlib.sha256(raw).hexdigest(),"aad":"listado20261027"}
 (pathlib.Path(os.environ["RUNNER_TEMP"])/"listado_cifrado.json").write_text(json.dumps(obj))
if __name__=="__main__":main()
