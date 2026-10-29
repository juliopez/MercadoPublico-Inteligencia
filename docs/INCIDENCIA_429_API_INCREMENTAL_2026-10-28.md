# Incidencia — lote incremental API, 28/10/2026

Se intentó una ejecución aislada y acotada de **una página de listado de Compra Ágil (01/10) y máximo dos detalles**. El servicio respondió HTTP **429 Too Many Requests** durante la ejecución. Workflow: https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/40798507220

## Estado verificado
- MER octubre, pestaña `Ofertas`: 18 filas de datos, en tres códigos COT.
- MER octubre, pestaña `Resultados`: 3 filas de datos.
- No se escribieron nuevas filas como resultado de esta ejecución.
- No se activó workflow nocturno; no se tocó cron 16:00.

## Acción y prevención
1. Suspender nuevos intentos en esta sesión: un HTTP 429 debe respetarse sin multiplicar solicitudes.
2. Registrar el intento como fallo recuperable `ERROR/HTTP_429` en control privado, con `proximo_intento` posterior al período de restricción según `Retry-After` si la respuesta lo incluye; de lo contrario backoff conservador.
3. Antes de próximas ejecuciones, incorporar lectura de `Retry-After`, presupuesto diario compartido y caché para evitar repetición de consultas.
4. No prometer que la limitación se resolverá exactamente a las 22:30: verificar los límites vigentes del ticket.
5. Conservar el primer lote completo del 28/10: `docs/CARGA_REAL_FASE2_MER_OCTUBRE_PRIMER_LOTE_2026-10-28.md`.
