# Recuperación Compra Ágil de fin de semana — 17/11/2026

## Objetivo
GitHub Actions, sin Ubuntu, inicia dos workflows independientes los sábados y domingos a las 20:00 de Chile. El disparador se programa con dos expresiones UTC por cambio de horario; la validación de hora chilena descarta la ejecución alternativa. Los schedules de GitHub pueden retrasarse: si se pierde la hora 20 local, la ejecución se omite y no se declara exitosa una recuperación.

## Workflows
- `.github/workflows/compra-agil-recuperacion-sabado.yml`
- `.github/workflows/compra-agil-recuperacion-domingo.yml`
- Selector: `scripts/seleccionar_recuperacion_fin_semana.py`.
- Ejecutor aislado: `scripts/mer_api_recuperacion_fin_semana.py`.

El selector recorre desde el día 1 del mes operativo hasta la fecha actual y elige la primera jornada cuyo checkpoint no tenga `completa=true`. No modifica los procesos diarios. La consulta utiliza los filtros `publicado_desde` y `publicado_hasta` para la fecha seleccionada; repetir por jornadas cubre el rango del mes, sin depender de un único listado masivo. El sábado o domingo siguiente retoma la jornada pendiente. No incluye meses archivados.

## Controles
- Concurrencia compartida `mer-api-actions-unica` para evitar choque con proceso nocturno.
- API: separación mínima 10 segundos, lotes máximo 400, dos reintentos; 429, 502, 503 y 504 detienen el lote después de tres respuestas y dejan pausa de una hora en checkpoint.
- Compara códigos de listados con Procesos del MER y evita solicitar detalles de procesos ya existentes; las inserciones verifican claves en MER. Ofertas y Resultados de procesos existentes no se reconsultan en este modo.
- Persiste checkpoint en `control/cola_api_mer.json` y publica cambios confirmados; exporta índices y dispara Pages incluso ante fallo de lote cuando es posible.
- No existe hora fija de cierre en el plan de negocio. **Limitación técnica:** cada ejecución de GitHub tiene duración máxima; el workflow reserva hasta cuatro horas para lotes y tiempo adicional para exportar/publicar. No hay encadenamiento automático ilimitado; la siguiente ejecución programada retoma.
- Un HTTP 429 o un listado no completado no equivale a recuperación exitosa. Comprobar `jornada_completa`, conteos MER y Pages.

## Estado
Implementación en PR de 17/11/2026. La primera ejecución real queda pendiente de auditoría; no afirmar recuperación de datos hasta disponer de logs, checkpoints, MER y Pages. La programación `schedule` de GitHub es aproximada y no garantiza inicio al minuto exacto.
