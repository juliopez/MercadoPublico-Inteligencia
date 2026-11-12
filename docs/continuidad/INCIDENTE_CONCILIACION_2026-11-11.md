# Incidente operativo 11/11/2026 — conciliación 09:00 y recuperación vespertina

**Estado documental:** recuperación de licitaciones completada; validación de corrección P7 y restauración del temporizador nocturno pendientes. Horario Chile (America/Santiago). Evidencia: capturas de terminal Ubuntu aportadas por el operador, código en main y GitHub Actions.

## Incidente y causa operativa observada
- El proceso de conciliación cronológica P7, programado a las 09:00, quedó retenido durante operaciones de Google Sheets, incluyendo respuesta 429 al retirar datos de OrdenesCompra de octubre. Mantuvo el candado MER y obstaculizó la ejecución ordinaria del ETL 16:00 y la carga/publicación de licitaciones 16:15. No confundir el disparador del ETL 16:00 con el AUX-1615.
- El proceso anterior fue detenido y se comprobó la liberación del candado MER en Ubuntu.
- PR #11 fusionado en main, commit `ee6f44b248615e5b98451acb9b266f03966a540a`: límite de reintentos P7 ante 429, control de plazo de las 14:00 entre tablas y estado de conciliación parcial verificada. Ubuntu actualizó main. **Limitación:** no es un timeout duro dentro de una operación de tabla; la primera validación operativa de estas mejoras corresponde a las 09:00 del 12/11. No declarar solucionado definitivamente.

## Recuperación manual P1 16:00 y AUX-1615
- Primer intento de cadena sin `--ejecutar`: el orquestador 16:00 usa `--verificar` por defecto, de modo que no acredita ejecución ETL. AUX recuperó 403 detalles, cargó 391 registros nuevos al MER y no publicó inicialmente por falta de carga ETL verificada posterior a las 16:00.
- Cadena corregida y ejecutada en Ubuntu: `bash scripts/ubuntu_cron_integrado.sh --ejecutar && bash scripts/ubuntu_recuperar_licitaciones_1615.sh`. El primer comando retornó 0 y permitió iniciar AUX, pero sus logs internos no fueron auditados exhaustivamente aquí.
- AUX continuó por lotes de 200 detalles, checkpoint persistente y carga/publicación progresiva. Salida final **22:37:38 Chile**: `PENDIENTES_API=0`, `LICITACIONES_API_PUBLICADAS`; exportación `procesos=8215`, `ordenescompra=58265` en catálogo operativo 2026-11; `EXPORTACION_V2_VERIFICADA`; push a main confirmado.
- Auditoría independiente GitHub: workflow `Publicacion V2 posterior al ETL Ubuntu` run [43135793186](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/43135793186) **success**; `Publicar participación histórica V2` run 43135793239 **success**; `Reparar analítica de organismos por período` run 43135850920 **success**; vista previa frontend run 43135911869 **success**. En main, `frontend-v2/data/participacion/2026-11/meta.json` reporta 8215 procesos. **No se verificó directamente el sitio Pages desde navegador externo**; éxito de workflows no equivale por sí solo a una inspección visual del frontend.

## Compra Ágil 22:05 — excepción de esta noche
- Temporizador correcto de usuario: `mercadopublico-api-github-dispatch.timer` (no es un timer de sistema). El operador ejecutó `systemctl --user stop mercadopublico-api-github-dispatch.timer` y comprobó `inactive` antes de las 22:05. No se modificó la definición ni la periodicidad.
- Se inició manualmente el workflow remoto `Compra Agil diaria 400 - cierre nocturno`, archivo `.github/workflows/api-compra-agil-400-actions.yml`, run **#26**, ID **43136762830**. Captura a las **22:54** muestra `In progress`. Se ejecuta en GitHub Actions, no en Ubuntu; **su resultado final aún no está verificado**.
- No ejecutar en paralelo el cron Ubuntu `scripts/cron_api_compra_agil_ubuntu.sh` mientras la ejecución remota esté activa. El timer local sigue suspendido hasta intervención del operador.

## Pendientes explícitos para jueves 12/11
1. Auditar ejecución P7 de las 09:00, duración, respuesta 429, liberación del candado y eventual estado parcial; comprobar que no bloquee 16:00/16:15.
2. Revisar resultado final y checkpoint del workflow Compra Ágil #26, cargas MER, publicación y Pages. Si falla, diagnosticar antes de repetir.
3. **Reactivar** temporizador de usuario con `systemctl --user start mercadopublico-api-github-dispatch.timer`; confirmar `active` y próxima activación 22:05 mediante `systemctl --user list-timers --all`. **No consta aún reactivado.** Comprobar que no coincida con una ejecución nocturna todavía activa.
4. Verificar frontend público directamente, especialmente noviembre, y, si se requiere auditoría integral, revisar logs de orquestador P1 de las 16:00.

## Protección
Registro exclusivamente documental: no cambiar ETL P1, AUX-1615, P7, API Compra Ágil, timers ni workflows por este incidente sin autorización. Distinguir hechos observados, comprobaciones indirectas y pendientes.
