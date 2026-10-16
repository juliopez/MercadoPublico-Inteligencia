import os
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

base = "https://api2.mercadopublico.cl/v2/compra-agil"
ticket = os.environ.get("CHILECOMPRA_TICKET", "")
if not ticket:
    raise SystemExit("Falta configurar CHILECOMPRA_TICKET")
tests = [
    ("listado", base + "?ttl_cambio_ms=300000"),
    ("detalle", base + "/425-325-COT26"),
]
for name, url in tests:
    started = time.monotonic()
    try:
        with urlopen(Request(url, headers={"ticket": ticket, "Accept": "application/json"}), timeout=30) as r:
            status = r.status
    except HTTPError as e:
        status = e.code
    except (URLError, TimeoutError) as e:
        status = type(e).__name__
    print(name, status, round(time.monotonic() - started, 2), flush=True)
