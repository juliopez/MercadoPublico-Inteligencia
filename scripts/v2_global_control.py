"""Control compartido V2 en Sheets. Usar bajo GitHub Actions concurrency global."""
from datetime import datetime,timedelta,timezone

HEAD=["servicio","fallos_consecutivos","suspendido_hasta_utc","siguiente_solicitud_utc","ultima_respuesta","actualizado_utc"]
def now():return datetime.now(timezone.utc)
def iso(t):return t.isoformat(timespec="seconds")
def load(ws):
    if ws.col_count<17:
        ws.add_cols(17-ws.col_count)
    header=ws.get("L1:Q1")
    if header and header[0] and header[0]!=HEAD:
        raise RuntimeError("ControlV2!L:Q ya ocupado por otra estructura")
    if not header or not header[0]:
        ws.update(range_name="L1:Q1",values=[HEAD],value_input_option="RAW")
    records=ws.get("L2:Q2")
    r=records[0] if records else []
    if r and r[0]!="api_v2":raise RuntimeError("Servicio de control V2 no reconocido")
    return r+[""]*(6-len(r))
def parse(s):
    return datetime.fromisoformat(s) if s else datetime.min.replace(tzinfo=timezone.utc)
def write(ws,r):
    ws.update(range_name="L2:Q2",values=[r],value_input_option="RAW")
def reserve(ws):
    r=load(ws);t=now()
    if parse(r[2])>t:
        print("V2_CIRCUITO_ABIERTO hasta",r[2]);return False
    if parse(r[3])>t:
        print("V2_FRECUENCIA_ESPERA hasta",r[3]);return False
    r[0]="api_v2";r[3]=iso(t+timedelta(seconds=60));r[5]=iso(t)
    write(ws,r)
    return True
def finish(ws,http):
    r=load(ws);n=int(r[1] or 0)
    temporary=http is None or http in (500,502,503,504)
    n=n+1 if temporary else 0
    until=now()+timedelta(seconds=3600 if http==429 else 1800) if http==429 or n>=3 else None
    r[0]="api_v2";r[1]=str(n);r[2]=iso(until) if until else "";r[4]=str(http if http is not None else "red");r[5]=iso(now())
    write(ws,r)
    print("V2_CONTROL_GLOBAL fallos=",n," suspendido=",r[2] or "no")
