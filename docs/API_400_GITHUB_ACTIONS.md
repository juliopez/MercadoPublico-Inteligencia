# Proceso 2 — Portabilidad de la ejecución API de 400 a GitHub Actions

**Estado a 31/10/2026:** workflow manual incorporado al repositorio; **no se ha ejecutado ningún lote productivo en GitHub Actions**. La línea base Ubuntu de 400 registros sigue protegida y sin cambios.

## Implementación
- Archivo: `.github/workflows/api-compra-agil-400-actions.yml`.
- Desencadenante exclusivo: `workflow_dispatch`, con parámetros `max_detail` (1–400) y `periodo` (AAAA-MM).
- Entorno alojado en GitHub Actions, `ubuntu-latest`, Python 3.11, máximo cinco horas, concurrencia de una ejecución API por workflow.
- Reutiliza **sin modificar** `scripts/mer_api_incremental_10.py` y el esquema MER.
- Recupera `control/cola_api_mer.json` versionada y respeta consulta mínima de 10 segundos, política 429 y deduplicación con MER Sheets.
- Conserva resultados y exporta con `scripts/exportar_mer_operativo_v2.py`.
- Regenera índices de búsqueda, perfiles, analítica y relaciones localmente, antes de un único commit/push de control y datos públicos.
- Despacha explícitamente `preview-frontend-v2.yml` tras el push: los pushes efectuados con `GITHUB_TOKEN` **no disparan otros workflows por push**. No se dispara el derivador existente para evitar colisiones.
- Bloquea el push si `main` cambió durante el lote, evitando sobrescribir silenciosamente otra ejecución. Un caso de conflicto requiere recuperación del estado local, no ejecutar el lote a ciegas.

## Configuración necesaria en GitHub
Crear en Settings → Secrets and variables → Actions (Repository secrets):
1. `CHILECOMPRA_TICKET` — ticket privado API.
2. `GOOGLE_SERVICE_ACCOUNT_JSON` — contenido JSON completo de una cuenta de servicio con acceso de escritura al Sheet MER de destino.

**No publicar valores de secretos en README, issues ni logs.** El token de GitHub es el `GITHUB_TOKEN` efímero con permisos `contents: write` y `actions: write`. Las políticas de Actions de la organización/repositorio también deben permitir ejecutar el workflow y publicar.

## Restricción histórica crucial
El motor probado verifica el mes calendario Santiago y autoriza un único MES operativo vigente, o una excepción del mismo mes archivado pendiente de conciliación. Por ello, el workflow incorporado aplica un **bloqueo explícito cuando `periodo` no coincide con el mes calendario vigente**; no se puede usar directamente en noviembre para seguir con `2026-10-01`. Tampoco repara automáticamente retrasos de un período histórico.

**Requisito siguiente para continuar el día 1 de octubre después del cambio mensual:** desarrollar y probar un modo de backfill retroactivo separado, limitado a un histórico específico pendiente de cierre oficial, sin alterar el motor Ubuntu protegido y con prohibición de escribir un octubre cerrado definitivamente. No eludir simplemente los bloqueos existentes.

## Advertencias y pruebas
- La concurrencia de GitHub Actions **no comparte** candado local con Ubuntu: evitar ejecutar simultáneamente el cron manual API y el workflow sobre el mismo MER y la misma cola, especialmente si Ubuntu tiene cambios locales no enviados.
- Comprobar las cuotas/429 de la API desde IP de runners hospedados por GitHub; 400 en Ubuntu no garantiza resultados idénticos en la red GitHub.
- La duración real 78m36s proviene de Ubuntu; el workflow no tiene aún tasa o prueba productiva propia.
- Las validaciones de workflow o su presencia en GitHub **no constituyen ejecución real, integración con secretos ni publicación verificada**.
- **No está programado horario nocturno y no se han activado consultas de forma automática.** Activar un lote requiere ejecución manual explícita en Actions y secretos disponibles.
- El cron de las 16:00, la línea base Ubuntu API 400, rotación y consolidación no se modificaron.
