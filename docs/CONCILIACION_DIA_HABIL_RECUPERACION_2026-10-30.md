# Conciliación mensual diferida — 10 o primer día hábil (Chile)

**Fecha:** 30/10/2026. **Estado:** preparación automatizada implementada en GitHub; unidades systemd NO instaladas/activadas en Ubuntu. La conciliación final de Sheets requiere revisión y aprobación.

## Regla recurrente
Cada mes, evaluar a partir del día 10 o primer día hábil posterior (excluye sábados, domingos y feriados nacionales de Chile). Comprobar a diario y al arranque Ubuntu mediante timer `Persistent=true`; si está apagado el día objetivo, reintentar en próxima sesión encendida. Si faltan fuentes oficiales, conservar estado pendiente y reintentar después.

## Archivos
- `config/feriados_chile_conciliacion.json`: calendario nacional **2026** verificado. Cada año siguiente debe verificarse su calendario previamente; años no verificados bloquean en lugar de asumir hábiles. Feriados regionales, si relevantes, deben incorporarse.
- `scripts/verificar_ventana_conciliacion.py`: cálculo de primer día hábil, estado de cierre y salida `PENDIENTE_CONCILIACION` o `NO_CORRESPONDE`.
- `scripts/ubuntu_preparar_conciliacion_persistente.sh`: candado compartido MER, orquestador oficial de descarga/importación y comprobación, sin aplicar ni mover Drive.
- `deploy/systemd/mercadopublico-conciliacion.service`, `deploy/systemd/mercadopublico-conciliacion.timer`: servicio/timer de **usuario**, propuesta de instalación. El servicio asume ruta de repositorio bajo `$HOME/Julio Lopez/chilecompra/MercadoPublico-Inteligencia`; ajustar antes de activar si cambió.
- `scripts/orquestar_cierre_mensual.py`: ahora permite preparar el mes anterior ya marcado `historico` tras rotación lógica. No autoriza aplicar sobre históricos.

## Antes de instalar en Ubuntu
```bash
cd "$HOME/Julio Lopez/chilecompra/MercadoPublico-Inteligencia"
git pull --ff-only origin main
.venv/bin/python scripts/verificar_ventana_conciliacion.py --fecha 2026-11-10
.venv/bin/python scripts/verificar_ventana_conciliacion.py --fecha 2026-11-08
bash -n scripts/ubuntu_preparar_conciliacion_persistente.sh
```

Revisar calendario, permisos de Drive y acceso a las tres fuentes. **No activar automáticamente** antes de validar el procedimiento de cierre operativo y la conciliación de octubre.

## Instalación propuesta, pendiente de validación y autorización operativa en Ubuntu
Crear `~/.config/systemd/user`; copiar allí los dos archivos `.service` y `.timer`. Ejecutar `systemctl --user daemon-reload`, después `systemctl --user enable --now mercadopublico-conciliacion.timer`. Comprobar `systemctl --user list-timers` y `journalctl --user -u mercadopublico-conciliacion.service`. Requiere sesión de usuario activa para el disparo al arranque; para funcionamiento independiente de inicio de sesión se evalúa `loginctl enable-linger` solo si es necesario.

## Límite deliberado
La automatización **prepara** los ZIP oficiales y los CSV de contraste; NO ejecuta la reconciliación final en Sheets, NO traslada archivos de Drive, NO declara histórico definitivo, y NO modifica el cron productivo de las 16:00. Para el cierre octubre del 10/11 seguir `docs/RUNBOOK_CIERRE_2026_10.md`, que exige verificación, respaldo, conciliación y autorización.

## Riesgo pendiente
La bandera `CONCILIACION_HISTORICA_VERIFICADA` en `estado_cierre.json` aún no la emite el flujo de cierre existente. Antes de autorizar operación desatendida completa hay que integrar la marca de finalización al cierre real y comprobar que no se repita indefinidamente en un mes ya finalizado. El preparador actual reutiliza descargas verificadas con hash.
