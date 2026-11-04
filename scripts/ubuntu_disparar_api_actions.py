#!/usr/bin/env python3
"""Disparador Ubuntu, independiente del cron ETL de las 16:00.

Solo solicita un workflow_dispatch; NO consulta ChileCompra ni escribe en Sheets.
Necesita gh autenticado con permiso actions:write en el repositorio.
"""
import argparse
import datetime as dt
import fcntl
import json
import os
import pathlib
import shutil
import subprocess
import sys
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Santiago")
REPO = "juliopez/MercadoPublico-Inteligencia"
WORKFLOW = "api-compra-agil-400-actions.yml"
LOCK = pathlib.Path(f"/tmp/mercadopublico-api-dispatch-{os.getuid()}.lock")


def jornada(ahora):
    local = ahora.astimezone(TZ)
    objetivo = local.date() if local.hour >= 22 else local.date() - dt.timedelta(days=1)
    ventana = local.hour >= 22 or local.hour < 5
    return objetivo, ventana and objetivo.weekday() < 5


def pertenece_a_jornada(run, objetivo):
    """Filtra solo inicios en la ventana nocturna de la jornada objetivo."""
    try:
        stamp = dt.datetime.fromisoformat(str(run["created_at"]).replace("Z", "+00:00")).astimezone(TZ)
    except (ValueError, TypeError, KeyError):
        return False
    inicio = dt.datetime.combine(objetivo, dt.time(22), TZ)
    fin = inicio + dt.timedelta(hours=7)
    return inicio <= stamp < fin


def comando_gh(*args):
    res = subprocess.run(["gh", *args], text=True, capture_output=True, timeout=45)
    if res.returncode != 0:
        msg = (res.stderr or res.stdout).strip()
        raise RuntimeError("GitHub CLI: " + msg[:500])
    return res.stdout


def ejecuciones():
    raw = comando_gh(
        "api", "-X", "GET",
        f"repos/{REPO}/actions/workflows/{WORKFLOW}/runs?per_page=40"
    )
    result = json.loads(raw)
    if not isinstance(result.get("workflow_runs"), list):
        raise RuntimeError("Respuesta API GitHub sin lista de ejecuciones")
    return result["workflow_runs"]


def decidir(runs, objetivo):
    """No iniciar si existe una ejecución activa O ya se lanzó la jornada.

    Una ejecución activa de otra fecha también bloquea, por concurrencia.
    """
    activos = [r for r in runs if r.get("status") in ("queued", "in_progress", "waiting", "pending", "requested")]
    if activos:
        return False, "EJECUCION_ACTIVA_" + str(activos[0].get("id", "?"))
    anteriores = [r for r in runs if pertenece_a_jornada(r, objetivo)]
    if anteriores:
        return False, "JORNADA_YA_DISPARADA_" + str(anteriores[0].get("id", "?"))
    return True, "DISPARO_PENDIENTE"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--verificar", action="store_true", help="Comprobar configuración y consultar GitHub, sin despachar")
    ap.add_argument("--ejecutar", action="store_true", help="Despachar una sola vez dentro de la ventana chilena")
    args = ap.parse_args()
    if args.verificar == args.ejecutar:
        ap.error("Escoge --verificar o --ejecutar")
    now = dt.datetime.now(TZ)
    objetivo, permitido = jornada(now)
    print("DISPARADOR_UBUNTU", "hora_chile=" + now.isoformat(),
          "jornada=" + objetivo.isoformat(), "autorizado=" + str(permitido), flush=True)
    if not shutil.which("gh"):
        raise SystemExit("FALTA_GH: instalar GitHub CLI y autenticar con permiso actions:write")
    if not permitido and args.ejecutar:
        print("OMITIDA_FUERA_VENTANA: no se solicita workflow_dispatch", flush=True)
        return
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    with LOCK.open("w") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        runs = ejecuciones()
        permitido_disparo, razon = decidir(runs, objetivo)
        print("ESTADO_GITHUB", razon, flush=True)
        if args.verificar:
            print("VERIFICACION_OK_SIN_DESPACHO", flush=True)
            return
        if not permitido_disparo:
            print("OMITIDA_SIN_DUPLICADOS", flush=True)
            return
        comando_gh("workflow", "run", WORKFLOW, "--repo", REPO, "--ref", "main")
        print("WORKFLOW_DISPATCH_SOLICITADO", "jornada=" + objetivo.isoformat(), flush=True)
        # GitHub puede tardar en crear la ejecución; no afirmar que procesó la API.


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        print("ERROR_DISPARADOR:", exc, file=sys.stderr, flush=True)
        sys.exit(1)
