# Vista unificada de Órdenes de Compra — frontend V2

**Estado:** código publicado en rama `main`; revisión visual y CI aún no confirmadas.

## Cambio aprobado

Se reemplazó la presentación dispersa de órdenes exactas, documentadas y candidatas por **una sola tabla de OC relacionadas** en la ficha de Procesos. La tabla ofrece código navegable, período, proveedor, monto disponible en la fuente, estado y criterio de relación.

- Prioridad por OC: **documentada (3) > referencia exacta `codigo_proceso` (2) > candidata por unidad y proveedor (1)**.
- Deduplicación por `codigo_oc`: una OC ocupa una fila aun cuando coincida por varios caminos.
- El contador de la pestaña muestra todas las OC relacionadas, mientras el subtítulo separa las verificadas y las candidatas.
- Las coincidencias estadísticas **no acreditan** adjudicación y aparecen claramente como candidatas; no se mezclan con los vínculos documentales.
- La interfaz reutiliza `data/vinculos-oc-verificados.json`, las relaciones exactas de índices y `data/oc-candidatas/`; no modifica las fuentes.

## Archivos modificados

`frontend-v2/js/app.js`: nueva función `showUnifiedOC`, consolidación y deduplicación, reemplazo de dos renderizadores anteriores.

`frontend-v2/index.html`: panel y etiqueta de pestaña unificados.

`frontend-v2/css/styles.css`: tabla adaptable con desbordamiento horizontal en pantallas pequeñas.

**No se modificaron** Google Sheets, históricos originales, ETL, cron, V1 ni mecanismo de carga de archivos.

## Control y límites

Se comprobó por lectura de código que la nueva función existe, se llama en `loadRelated`, se retiran los renderizadores previos y el contador se calcula tras deduplicar. La validación sintáctica local con Node no se pudo ejecutar porque el entorno no resolvió el dominio de descarga; **no declarar pruebas automáticas o revisión visual aprobadas** sin evidencia de GitHub Actions o navegación real.

Caso visual recomendado: `1028871-59-COT26`. Debe mostrar como documentada la OC `1028871-369-AG26` y como candidata separada `1028871-390-AG26`, sin duplicación. La revisión visual debe verificar carga, clic hacia detalle, contador total y columnas en móvil.

La homologación de la conciliación integral junio/julio/septiembre es independiente; sus candidatos nunca deben elevarse a vínculo documental sin evidencia.
