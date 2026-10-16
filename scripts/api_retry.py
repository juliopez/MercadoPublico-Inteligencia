"""Recuperación acotada ante fallas temporales de la API ChileCompra."""
import json, time, os
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

TEMPORARY=(429,502,503,504)

def fetch_json(req, timeout=50, label="API", attempts=3):
    attempts=max(1,min(3,int(os.getenv("API_MAX_ATTEMPTS",str(attempts)))))
    last_error=None
    for i in range(attempts):
        try:
            with urlopen(req,timeout=timeout) as response:
                data=json.load(response)
            if i:
                print(f"::notice title=API recuperada::{label}: exitosa tras {i+1} intentos",flush=True)
            return data
        except HTTPError as err:
            last_error=err
            code=err.code
            if code not in TEMPORARY:
                print(f"::error title=Error no recuperable::{label}: HTTP {code}. Revisar credenciales y petición; no reintentar automáticamente.",flush=True)
                raise
            reason=f"HTTP {code}"
            retry=err.headers.get("Retry-After","") if err.headers else ""
            delay=min(120,int(retry)) if retry.isdigit() else (30,60,120)[min(i,2)]
        except (URLError,TimeoutError) as err:
            last_error=err
            reason=type(err).__name__
            delay=(30,60,120)[min(i,2)]
        if i+1==attempts:
            print(f"::error title=API no disponible::{label}: {reason} tras {attempts} intentos. No se completó la consulta; espere unos minutos y vuelva a ejecutar manualmente.",flush=True)
            raise last_error
        print(f"::warning title=Reintento de API::{label}: {reason}; intento {i+1}/{attempts}, nueva consulta en {delay}s",flush=True)
        time.sleep(delay)
