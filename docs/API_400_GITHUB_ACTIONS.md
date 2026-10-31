# Proceso 2 — Portabilidad de la ejecución API de 400 a GitHub Actions

> **Auditoría de la primera prueba del 31/10/2026:** [400/400 consultas finalizadas; fallo posterior antes de publicar cola y Pages](RESULTADO_PRUEBA_API_400_ACTIONS_2026-10-31.md). El código del wrapper fue corregido sin repetir el lote. **No volver a ejecutar hasta recuperar/reconciliar su estado incremental.**

**Estado a 31/10/2026:** se verificaron 400 consultas en Actions el 31/10, pero falló la validación posterior por variable de período vacía. Se corrigió y se habilitó la programación nocturna; **la cadena completa de publicación todavía no ha superado una prueba productiva de extremo a extremo**. La línea base Ubuntu continúa intacta.

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

## Operación nocturna desatendida (configuración del 31/10/2026)

- Calendario: **turnos cuyo día de inicio es lunes a viernes**, siempre en **America/Santiago**. Ventana 22:00–07:00 del día siguiente.
- Seis oportunidades por noche: **22:00, 23:30, 01:00, 02:30, 04:00 y 05:30**, con margen de 20 minutos por retrasos de disparo GitHub. Un lote admite máximo 400 detalles y mantiene 10 segundos mínimos entre peticiones. No se inicia automáticamente en fin de semana.
- La regla horaria se evalúa después de que GitHub emite un cron UTC cada 30 minutos en la ventana amplia. El comienzo y duración reales dependen del servicio GitHub Actions; **no existe garantía estricta de terminar antes de las 07:00** si el lote demora más de lo medido.
- Al cambiar el mes mientras la noche está en curso, se bloquean turnos posteriores a medianoche del mes nuevo que intentarían representar el anterior. La cola actual trabaja con cursor progresivo dentro del mes operativo y **no restringe exclusivamente a la fecha de inicio del turno**: prioriza continuidad y pendientes, evitando saltarse páginas. No declarar implementado todavía un filtro diario estricto por publicación.
- Una sola ejecución activa o encolada por grupo de concurrencia del workflow. No ejecutar al mismo tiempo el procedimiento Ubuntu manual sobre el mismo Sheets y cola.
- **Nueva salvaguarda:** inmediatamente después de completar el motor y verificar que el informe corresponde a esta ejecución y período, se hace commit y push de `control/cola_api_mer.json` y `control/ultimo_reporte_api_mer.json` **antes** de exportar los datos públicos; además se adjunta un artefacto de respaldo del estado aun cuando fallen pasos posteriores. Solo entonces se intenta la exportación y publicación.
- El disparo de Pages es explícito porque un push con `GITHUB_TOKEN` no genera automáticamente nuevos workflows por evento push. El despliegue puede seguir pendiente o fallar: revisar la ejecución de `preview-frontend-v2.yml`.
- Si GitHub `main` cambia durante una ejecución, un bloqueo impide publicar sobre estado concurrente. El artefacto conserva el reporte/cola para conciliación; **este conflicto no se resuelve todavía de forma desatendida**.
- El **lote 400 de octubre del 31/10** dejó Sheets potencialmente actualizado pero su checkpoint no fue publicado. Esta corrección **no recupera automáticamente aquel checkpoint histórico**. Debe conciliarse aparte antes de reanudar octubre: [auditoría de la falla](RESULTADO_PRUEBA_API_400_ACTIONS_2026-10-31.md).
- Programación recurrente activada por commit del workflow, **primera ejecución programada todavía no verificada**. No confundir con certificación de operación productiva completa.

### Condiciones que faltan para declarar el flujo plenamente desatendido

1. Verificar una noche real y el éxito de todos los pasos hasta GitHub Pages, incluyendo los conteos del Sheet.
2. Reconciliar los 400 de octubre del intento fallido y su cursor (histórico pendiente).
3. Comprobar el resultado de un conflicto de ramas o pérdida de red al guardar el checkpoint; hoy hay resguardo de estado, pero puede requerir recuperación manual.
4. Validar desempeño temporal y volumen diario, especialmente retrasos de GitHub y límites HTTP 429.
5. Revisar eventual requisito de limitar cada ejecución estrictamente a la fecha de publicación del día de inicio, sin perder recuperación histórica. El motor protegido no se modificó para imponerlo.

## Requisito operativo acordado: desde lunes 02/11/2026

**Objetivo obligatorio (todavía no implementado en su totalidad):** captar todos los procesos Compra Ágil publicados en la fecha objetivo del turno, en lotes de máximo 400, hasta agotar el listado del día; escribir y verificar MER del **mes operativo**, generar derivados y **comprobar** despliegue de GitHub Pages. La fecha objetivo de las 22:00 debe conservarse al cruzar medianoche; no basta con consultar fechas pendientes desde el primer día de mes. El límite 07:00 es de **no iniciar nuevas consultas** fuera de la franja y conservar cualquier pendiente. Evitar declarar cierre del día si faltan páginas, detalles o publicación.

**Brechas constatadas del workflow actual**: seis disparos programados sin lógica de terminación por agotamiento del día; motor con cursor del mes en vez de filtro fijo día; comprobación de Pages no incluida; salvaguardas de conflicto de commits pendientes; sin verificación integral de primer turno real. No considerar estos puntos resueltos por la sola presencia del schedule.

**Líneas base**: no modificar el ETL 16:00, el ejecutor Ubuntu validado, la rotación 19:00 ni la conciliación histórica 10:00 para este cambio; implementarlo en componentes Actions específicos con validación productiva.
