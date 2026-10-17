"""Cliente HTTP compartido: ritmo moderado y corte inmediato ante HTTP 429."""
import json, os, time
from pathlib import Path
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

class RateLimited(RuntimeError):
    def __init__(self, label, retry_after=None):
        super().__init__(f"HTTP 429 en {label}; detener lote y reanudar posteriormente")
        self.retry_after=retry_after

_LAST_CALL=0.0
def _pace():
    global _LAST_CALL
    seconds=max(0.0,float(os.getenv("API_MIN_INTERVAL_SECONDS","1.5")))
    remain=seconds-(time.monotonic()-_LAST_CALL)
    if remain>0:time.sleep(remain)
    _LAST_CALL=time.monotonic()

def _retry_after(headers):
    value=(headers.get("Retry-After") if headers else None) or ""
    try:return max(0,int(value))
    except (ValueError,TypeError):pass
    try:return max(0,int((parsedate_to_datetime(value)-datetime.now(timezone.utc)).total_seconds()))
    except (ValueError,TypeError,OverflowError):return None

def fetch_json(req,timeout=50,label="API",attempts=3):
    attempts=max(1,min(3,int(os.getenv("API_MAX_ATTEMPTS",str(attempts)))))
    for i in range(attempts):
        _pace()
        try:
            with urlopen(req,timeout=timeout) as response:
                return json.load(response)
        except HTTPError as err:
            if err.code==429:
                retry=_retry_after(err.headers)
                Path('.api_rate_limited').write_text(json.dumps({'origen':label,'retry_after':retry}),encoding='utf-8')
                print(f"::error title=ChileCompra limitó consultas::{label}: HTTP 429. Retry-After={retry}; detener lote sin probar otro código.",flush=True)
                raise RateLimited(label,retry) from err
            if err.code not in (502,503,504):raise
            if i+1==attempts:raise
            delay=(10,30)[min(i,1)]
            print(f"::warning::{label}: HTTP {err.code}, reintento {i+2}/{attempts} en {delay}s",flush=True)
            time.sleep(delay)
        except (URLError,TimeoutError):
            if i+1==attempts:raise
            time.sleep((10,30)[min(i,1)])
