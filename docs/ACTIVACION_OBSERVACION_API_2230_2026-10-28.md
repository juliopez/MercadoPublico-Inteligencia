# Activación de observación nocturna API — 28 octubre 2026

## Qué está activo
- Workflow `.github/workflows/observacion-api-2230.yml` incorporado a `main`.
- Programación: a las 01:30 y 02:30 UTC, **guardia interna** de lunes a viernes entre 22:25 y 22:55 `America/Santiago`, para adaptarse a cambios de horario.
- Solo una página de listado (10 entradas) y **máximo dos detalles** publicados en octubre 2026.
- Uso del secreto ya empleado por pilotos `CHILECOMPRA_TICKET`.
- Si recibe HTTP 429, abandona el lote; no intenta una ráfaga de reintentos.
- Respuestas completas únicamente en artefacto **cifrado** temporal (7 días); el log contiene métricas no personales.

## Qué no está activo
- No hay escritura nocturna en la hoja MER: esta es una observación, no una carga.
- No hay persistencia de cola ni cursor entre ejecuciones: no prometer avance real diario del backfill.
- No se ejecuta la importación mensual de `Procesos`.
- No se toca el cron Ubuntu 16:00 ni el workflow de publicación ya validado.
- La ejecución programada de GitHub Actions puede tener demoras o no dispararse a la hora exacta; no afirmar que una ejecución ha ocurrido hasta comprobar su registro.

## Verificación
Workflow: https://github.com/juliopez/MercadoPublico-Inteligencia/actions/workflows/observacion-api-2230.yml
Tras las 22:30 Santiago consultar estado, log y artefacto cifrado; recién después decidir la integración de la escritura al MER aprovechando las credenciales Ubuntu existentes.
