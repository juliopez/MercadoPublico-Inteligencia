#!/usr/bin/env python3
"""Autorizar API nocturna según hora REAL de ejecución en Santiago.

La jornada objetivo es la fecha chilena del inicio nocturno: entre 22 y 23
es hoy; entre 00 y 04:59 es ayer. Así un schedule demorado no se descarta.
No ejecuta consultas ni escribe en Google Sheets.
"""
import datetime as dt
import os
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Santiago")

def evaluar(ahora):
    if ahora.tzinfo is None:
        raise ValueError("Se requiere fecha con zona horaria")
    chile = ahora.astimezone(TZ)
    objetivo = chile.date() if chile.hour >= 22 else chile.date() - dt.timedelta(days=1)
    en_ventana = chile.hour >= 22 or chile.hour < 5
    autorizado = en_ventana and objetivo.weekday() < 5
    motivo = ("FUERA_VENTANA" if not en_ventana else
              "JORNADA_FIN_SEMANA" if objetivo.weekday() >= 5 else
              "AUTORIZADA")
    return autorizado, objetivo, motivo

def main():
    ahora = dt.datetime.now(TZ)
    permitido, objetivo, motivo = evaluar(ahora)
    print("VENTANA_API_CHILE", ahora.isoformat(),
          "OBJETIVO", objetivo.isoformat(),
          "ESTADO", motivo, flush=True)
    salida = os.getenv("GITHUB_OUTPUT")
    if salida:
        with open(salida, "a", encoding="utf-8") as f:
            f.write("ok=" + str(permitido).lower() + "\n")
    if permitido:
        env = os.getenv("GITHUB_ENV")
        if env:
            with open(env, "a", encoding="utf-8") as f:
                f.write("MER_API_FECHA_OBJETIVO=" + objetivo.isoformat() + "\n")
                f.write("PERIODO_SOLICITADO=" + objetivo.strftime("%Y-%m") + "\n")

if __name__ == "__main__":
    main()
