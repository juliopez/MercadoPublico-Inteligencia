#!/usr/bin/env python3
"""Selecciona la jornada más antigua aún no completada del mes operativo.
Tolera retrasos del schedule y evita duplicar el cron UTC de otra estación.
No consulta la API ni modifica el MER.
"""
import datetime as dt
import json
import os
import pathlib
import sys
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Santiago")
ROOT = pathlib.Path(__file__).resolve().parents[1]

def seleccionar(ahora, dia, state, periodo):
    chile = ahora.astimezone(TZ)
    esperado = 5 if dia == "sabado" else 6
    # GitHub puede retrasar el schedule varias horas, incluso hasta el día siguiente.
    # El disparador de 23:00 UTC corresponde a verano (UTC-3);
    # el de 00:00 UTC corresponde a invierno (UTC-4).
    # Se valida la hora UTC prevista, NO la hora efectiva del runner.
    cron = os.getenv("MER_RECOVERY_SCHEDULE_CRON", "").strip()
    if cron:
        try:
            hora_utc = int(cron.split()[1])
        except (IndexError, ValueError):
            return None
        if hora_utc not in (0, 23):
            return None
        candidatos = [chile.date() - dt.timedelta(days=i) for i in range(3)]
        fecha_programada = None
        for fecha_candidata in candidatos:
            if fecha_candidata.weekday() != esperado:
                continue
            prevista = dt.datetime.combine(fecha_candidata, dt.time(20), TZ)
            if prevista.astimezone(dt.timezone.utc).hour != hora_utc:
                continue
            retraso = (ahora - prevista).total_seconds()
            if 0 <= retraso <= 36 * 3600:
                fecha_programada = fecha_candidata
                break
        if fecha_programada is None:
            return None
    else:
        # Disparo manual: permitir reintentos del fin de semana sin ventana horaria.
        fecha_programada = chile.date()
        if fecha_programada.weekday() != esperado:
            return None
    if periodo != fecha_programada.strftime("%Y-%m"):
        return None
    jornadas = state.get("jornadas_actions", {})
    inicio = fecha_programada.replace(day=1)
    for desplazamiento in range((fecha_programada - inicio).days + 1):
        fecha = (inicio + dt.timedelta(days=desplazamiento)).isoformat()
        if not jornadas.get(fecha, {}).get("completa", False):
            return fecha
    return None

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("sabado", "domingo"):
        raise SystemExit("Uso: seleccionar_recuperacion_fin_semana.py sabado|domingo")
    ahora = dt.datetime.now(TZ)
    catalogo = json.loads((ROOT / "config/catalogo_sheets.json").read_text())
    activos = [p for p,v in catalogo["periodos"].items() if v.get("tipo") == "operativo"]
    if len(activos) != 1:
        raise SystemExit("BLOQUEO: catálogo operativo ambiguo")
    archivo = ROOT / "control/cola_api_mer.json"
    state = json.loads(archivo.read_text()) if archivo.exists() else {}
    fecha = seleccionar(ahora, sys.argv[1], state, activos[0])
    print("RECUPERACION", sys.argv[1], "CHILE", ahora.isoformat(), "OBJETIVO", fecha or "SIN_AUTORIZACION_O_PENDIENTES", flush=True)
    if os.getenv("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write("ok=" + ("true" if fecha else "false") + "\n")
    if fecha and os.getenv("GITHUB_ENV"):
        with open(os.environ["GITHUB_ENV"], "a") as f:
            f.write("MER_API_FECHA_OBJETIVO=" + fecha + "\n")
            f.write("PERIODO_SOLICITADO=" + activos[0] + "\n")

if __name__ == "__main__":
    main()
