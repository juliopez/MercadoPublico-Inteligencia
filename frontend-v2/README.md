# Frontend V2 — Guía funcional y estado vigente

**Revisión:** 23-10-2026. **[Abrir V2](https://juliopez.github.io/MercadoPublico-Inteligencia/frontend-v2/)** · [README del proyecto](../README.md) · [Índice documental](../docs/INDICE_DOCUMENTACION.md).

V2 es un **frontend paralelo** que publica extractos autorizados de Mercado Público. V1 continúa operando desde `../index.html`; no se modifica por el desarrollo V2.

## Cómo utilizarlo

1. Seleccionar **entidad** y, para la exploración por bloques, un **mes de referencia** (Procesos, Ofertas, Resultados u Órdenes de compra).
2. Para explorar rápidamente, pulsar **Mostrar registros del período**: carga el primer bloque (hasta 1.000 registros), presenta páginas de **10** y desplaza a la tabla de resultados. La exploración por bloques y sus filtros locales están en el panel avanzado.
3. Para localizar un código, organismo o proveedor entre **todos los períodos publicados** (o uno solo), utilizar la **búsqueda global indexada**, que comprueba candidatos leyendo únicamente fragmentos necesarios. Puede incluir filtros según entidad. Las sugerencias son ayudas, no listas exhaustivas.
4. En la ficha de un registro, revisar resumen y campos desplegables; cuando existe un **código de proceso**, consultar mediante **pestañas con contadores** los Procesos, Ofertas, Resultados y OC relacionados en todos los meses publicados (junio–octubre 2026), con mes de origen visible.
5. **Evolución mensual**: seleccionar una barra para examinar un período, comparar otro mes y cambiar perspectiva entre actividad, montos informados y actores frecuentes. Las vistas de **actores y montos** presentan gráficos horizontales, no listados extensos.
6. Herramientas complementarias: perfiles de actores, comparación de hasta tres proveedores con sugerencias de razones sociales, favoritos guardados **solo en el navegador** y exportación CSV.

## Cobertura y límites

- Catálogo de verdad: [`data/catalogo-publico.json`](data/catalogo-publico.json). Históricos junio–septiembre; octubre 2026 **parcial**; faltan Ofertas y Resultados de octubre según catálogo.
- Las seis tablas internas MER son distintas de las **cuatro entidades** publicadas en el frontend.
- El navegador no accede a Google Sheets privadas ni descarga todos los históricos. Se leen fragmentos de unas 1.000 filas bajo demanda. Índices estáticos permiten búsquedas y relaciones entre meses.
- Las búsquedas globales requieren término/código; los filtros de estado y modalidad no son consultas autónomas por faceta. Paginación: 10 filas. Orden global: sobre coincidencias **ya verificadas**.
- Los perfiles agregados y rankings se basan en **nombres normalizados**, no identidad única por RUT. Los montos son importes **informados**, no pagos o contratos confirmados. Algunas entidades tienen campos monetarios sin valor informado.
- El enlace a la ficha oficial se muestra solo cuando hay una URL verificada o una ruta de licitación compatible; no se presupone que una Compra Ágil tenga URL de licitación.
- Las relaciones multimes abarcan **meses publicados en el catálogo**, no la totalidad de ChileCompra. Una asociación por código no acredita por sí sola adjudicación.
- CSV local exporta el bloque filtrado; CSV global verifica todos los candidatos antes de exportar y rechaza consultas que superen el límite explícito de 20.000.
- Octubre es parcial: evitar conclusiones sobre tendencias respecto a meses completos.

## Arquitectura pública y archivos

| Archivo/directorio | Propósito |
|---|---|
| `index.html`, `css/styles.css`, `js/app.js` | Interfaz, tablas y fragmentos |
| `js/busqueda-global.js` | Índice de prefijos y resultados progresivos |
| `js/sugerencias-global.js` | Sugerencias de palabras y facetas |
| `js/comparar-proveedores.js` | Comparación de actores por período |
| `js/analitica-interactiva.js` | Meses, vistas y agregados analíticos |
| `data/partes/`, `data/catalogo-publico.json` | Extractos y catálogo de recuentos |
| `data/busqueda/`, `data/indices/`, `data/relaciones-procesos/` | Índices de búsqueda y relaciones |
| `data/perfiles/`, `data/autocompletar/`, `data/analitica/`, `data/sugerencias/` | Agregados públicos y sugerencias |
| `../scripts/exportar_frontend_v2.py` | Exportación controlada de datos |
| `../scripts/generar_analitica_v2.py`, `../scripts/indexar_relaciones_procesos_v2.py` | Generación de agregados/índices |

**No** editar a mano los JSON generados ni mezclar V1 y V2. Los índices y agregados deben mantenerse sincronizados con el catálogo y los fragmentos mediante sus workflows específicos.

## Estado funcional y procedimientos para continuar

| Área | Comportamiento vigente |
|---|---|
| Entrada | «Mostrar registros del período» carga el primer bloque sin abrir el panel avanzado |
| Búsqueda global | Busca códigos y palabras en el mes completo usando índices; presenta progreso de candidatos y filtros pertinentes |
| Evolución mensual | Barras seleccionables, perspectivas de actividad/montos/actores y comparación con otro mes |
| Fichas | Resumen principal, detalle expandible, códigos navegables y relaciones históricas multimes |
| Relaciones | Procesos, Ofertas, Resultados y OC de todos los períodos públicos disponibles; el mes de origen aparece en cada tabla |
| Moneda | Campos monetarios visibles en CLP, conservando valores originales en los JSON |
| Perfil y comparación | Nombres normalizados, sugerencias y agregados por período; no identidad única por RUT |
| CSV | Bloque filtrado o búsqueda global completamente verificada dentro del límite establecido |

**Última comprobación técnica:** [validación de analítica y relaciones históricas](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39682682170) y [publicación de índices exactos de Procesos](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39682406233). CI no sustituye revisión manual del navegador ni auditoría integral.

### Dónde cambiar cada parte

- `js/app.js`: período, bloques, tablas, fichas, relaciones multimes, formatos y navegación.
- `js/busqueda-global.js`: consulta indexada de palabras y códigos, filtros y exportación global.
- `js/analitica-interactiva.js`: selección de meses, comparación y perspectivas.
- `js/comparar-proveedores.js`: comparación y sugerencias de proveedores.
- `js/sugerencias-global.js`: sugerencias de búsquedas y facetas.
- `css/styles.css`: presentación, responsividad y accesibilidad.
- `../scripts/generar_analitica_v2.py` y `../scripts/indexar_relaciones_procesos_v2.py`: agregados e índices generados fuera del navegador.

**Para ampliar períodos:** publicar primero extractos y catálogo reconciliados, después actualizar índices/agregados y comprobar la integración. Nunca editar manualmente grandes JSON ni depender de descargar el mes completo en cliente.

## Pruebas y documentación

- [Línea base de rendimiento y navegación](../docs/BASELINE_FRONTEND_V2_2026-10-21.md)
- [Búsqueda global](../docs/BUSQUEDA_GLOBAL_V2_2026-10-21.md)
- [Perfiles y comparador](../docs/PERFILES_CONTEXTUALES_FRONTEND_V2_2026-10-21.md)
- [Mejoras de experiencia](../docs/MEJORAS_UX_INTEGRALES_V2_2026-10-21.md)
- [Analítica interactiva y relaciones multimes](../docs/ANALITICA_INTERACTIVA_RELACIONES_HISTORICAS_V2_2026-10-21.md)

Las pruebas de sintaxis e integración GitHub Actions **no equivalen a validación de navegador en todos los casos**. La auditoría integral de UX, rendimiento, seguridad y compatibilidad con V1 sigue pendiente como tarea independiente.

La cronología completa de implementación se conserva en documentos especializados de `../docs/` y en el historial Git; no repetirla en este README.

## Búsqueda transversal por participantes

La sección **Participación histórica de empresas y organismos** permite consultar por nombre normalizado todos los meses publicados (junio–octubre de 2026), con sugerencias, totales, gráfico mensual y accesos a las ofertas o procesos del mes. Incluye métricas de **procesos distintos por proveedor dentro de cada mes** y de **ofertas recibidas vinculadas por código al organismo dentro del mismo mes**, siempre que los índices generados estén disponibles. No equivale a identificación única por RUT ni a una deduplicación de procesos entre meses. Referencia: [documentación de participantes históricos](../docs/PARTICIPANTES_HISTORICOS_V2_2026-10-21.md).


## Relaciones CA–OC y cambios recientes

- [Enriquecimiento por descripciones OC](../docs/ENRIQUECIMIENTO_OC_DESCRIPCIONES_2026-10-21.md): 1.411 relaciones nuevas incorporadas y verificadas en MER, más una documental previa; 54 casos separados para revisión. No confundir con candidatos por similitud.
- [Vista unificada de OC](../docs/VISTA_UNIFICADA_OC_FRONTEND_V2_2026-10-21.md): tabla única por OC con prioridad documental > referencia estructurada > candidata, sin duplicados y con contadores por certeza. La validación visual completa sigue siendo un hito diferente.
- [Búsqueda transversal multimes](../docs/BUSQUEDA_TRANSVERSAL_MULTIMES_V2_2026-10-21.md): todos los períodos por defecto, filtro mensual opcional, columna de período y apertura del detalle del mes real. La incidencia de «Ver detalle» quedó corregida en código; la aprobación visual posterior no consta.
- [Conciliación integral de junio, julio y septiembre](../docs/HOMOLOGACION_CONCILIACION_CA_OC_2026-10-21.md): motor y workflow publicados; verificar resultados antes de darla por concluida.

Las reglas de presentación no modifican `codigo_proceso` original, adjudicaciones, pagos, históricos, cron o ETL. La observabilidad y enriquecimiento incremental de nuevas cargas se analizarán conforme al [plan del cron de las 16:00](../docs/PLAN_MEJORAS_CRON_1600_2026-10-21.md).

## Comparación transversal de proveedores (23-10-2026)

El alcance predeterminado es **todos los períodos publicados**, independiente del mes utilizado para consultar registros. La opción **Mes específico** habilita un selector propio de comparación. Se emplean los agregados históricos e índices de participación ya publicados; no requiere ejecutar ETL ni modificar Google Sheets. La tasa de selección utiliza códigos de proceso únicos. La selección registrada no acredita por sí sola una adjudicación contractual, y los montos se presentan con sus límites de cobertura.

### Interpretación de resultados y autocompletado (23-10-2026)

La interfaz aclara que el valor **0** indica ausencia de registros coincidentes **en la cobertura publicada**, no ausencia absoluta de actividad del proveedor. Ofertas y órdenes de compra son entidades diferentes. El autocompletado informa expresamente el alcance efectivo (todos los períodos o un mes), con concordancia singular/plural. Cambio exclusivamente visual y de ayuda; sin alteraciones en ETL, datos, índices ni indicadores.

## Filtro temático del bloque 02 (31-10-2026)

El control «Comparar con» del panel de evolución mensual se sustituye por un formulario de palabras clave. En blanco mantiene los agregados generales; al aplicar, el módulo `js/analitica-filtro.js` consulta los índices públicos de búsqueda por cada mes y entidad, recupera solamente los fragmentos candidatos, verifica las palabras completas sobre los campos indexados y calcula los agregados de gráficos tras finalizar **todos** los períodos. Sin topes silenciosos ni resultados parciales presentados como totales. Al cambiar entidad o limpiar, se restauran los gráficos generales. La selección de una barra mensual se mantiene. «Comparar proveedores» es independiente y no se altera.

La búsqueda de palabras exige al menos tres caracteres y su alcance semántico coincide con el índice global: campos de código, nombre, organismo o proveedor, según la entidad. No se interpreta como búsqueda libre en todos los campos. Si algún índice o fragmento falla, el filtro no se aplica; se conserva el estado gráfico anterior. La ejecución con términos muy frecuentes puede implicar numerosas lecturas y una espera mayor que los agregados precalculados. Se recomienda comprobar consultas reales antes de declarar validación visual o rendimiento certificado.

## Ajustes UX del bloque 02 — 31-10-2026

1. Se elimina el mensaje «Mes de referencia»: los períodos se identifican dentro de los gráficos y en la acción contextual.
2. «Ver registros de AAAA-MM» se habilita únicamente después de elegir explícitamente una barra. Con filtro temático activo traslada mes, entidad y término a la búsqueda global indexada con alcance de un mes y ejecuta la consulta. Sin término, conduce a la exploración general del mes (primer bloque paginado), sin sugerir falsamente un listado mensual completo.
3. El filtro temático presenta una barra de progreso accesible: fase de planificación de índices (0–30 %) y fase de verificación de fragmentos candidatos (30–100 %), cuyo denominador se conoce antes de empezar a descargar fragmentos. El 100 % se muestra solo tras verificar todos los candidatos. Error y cancelación por cambio de entidad/limpieza no presentan cifras parciales como totales.

**Alcance:** HTML y JS de frontend V2. V1, workflows, ETL, ZIP históricos y cuatro procesos protegidos permanecen inalterados. Pruebas visuales y de Pages deben verificarse por separado de la integración del código.

## Indicadores inequívocos y concursos únicos (31-10-2026)

Las dos tarjetas de cobertura se rotulan por entidad e incorporan ayudas desplegables accesibles con sus unidades de conteo, cobertura y límites. No deben interpretarse las filas de ofertas o resultados como concursos. En Procesos se añade un panel específico para el mes seleccionado: códigos únicos, licitaciones, Compra Ágil y otras modalidades. El filtro temático deduplica por código y clasifica la modalidad de cada proceso; los valores del agregado general se publican al regenerar los JSON mensuales mediante el generador actualizado (`version:2`, campos `procesos_unicos` y `modalidades_unicas`). Mientras esos JSON no estén regenerados, no se presenta una cifra de procesos únicos no comprobada: se indica su indisponibilidad y se conservan las métricas anteriores. Los conteos representan coincidencias literales y cobertura publicada, no búsqueda semántica.

## Ofertas vinculadas y monto deduplicado por palabra clave (31-10-2026)

Al filtrar la entidad Procesos se identifican códigos únicos de los procesos coincidentes y, para cada mes, se consulta el índice público `data/indices/AAAA-MM.json` para localizar **ofertas de esos mismos códigos en ese mismo período**. Las ofertas se deduplican por `id_cotizacion` (clave mensual), no por proveedor. El monto ofertado suma importes válidos de ofertas únicas; se reporta el número de ofertas con importe y cualquier fila sin ID excluida. Si falla algún índice/fragmento, el resultado filtrado completo no se publica. Se agregan tooltips de suma de montos por entidad y promedio mensual, distinto de media por concurso. El presupuesto de procesos coincidentes se suma por código único por mes. No existe búsqueda semántica; los vínculos intermensuales quedan fuera del conteo de ofertas de ese mes. La carga de muchos códigos puede requerir tiempo adicional; verificar rendimiento real antes de certificarlo. No se cambian ETL, Sheets ni procesos protegidos.

## Ranking de organismos con concursos únicos (31-10-2026)

Para la entidad Procesos, el ranking central utiliza `organismos_procesos_unicos` en lugar de sumar filas de `top_actores_monto`. El presupuesto disponible se agrega una sola vez por código de proceso y mes, con el nombre del organismo informado en el primer registro del código. Cada barra incluye un desglose verificable de cantidad de procesos únicos, licitaciones, Compras Ágiles, otras modalidades y concursos con monto informado. Con filtro, los agregados proceden de procesos que cumplieron la búsqueda literal. Sin filtro, el script de agregados genera los campos en versión 3; los JSON aún no regenerados presentan una explicación en vez de una falsa barra de presupuesto único. Un organismo con distintas variantes de nombre puede aparecer separado; no se homogeniza automáticamente. Se preservan ETL, cron, API, consolidación y V1.


## Índice compacto de ofertas por proceso (optimización, 31-10-2026)

Se agregó `scripts/generar_indice_ofertas_por_proceso.py` para preagregar ofertas públicas **por mes y código exacto de proceso**. Recorre cada fragmento de la entidad Ofertas una sola vez en la etapa offline, deduplica `id_cotizacion` por proceso, conserva el número de ofertas únicas, el número con monto válido, el monto ofertado total y filas sin identificador. Comprueba el conteo de filas contra el catálogo público. Escribe `data/analitica-ofertas/AAAA-MM/meta.json` y archivos `00.json`–`ff.json` por primer byte del SHA-256 del código normalizado. No toca ETL, Sheets, API, cron ni los cuatro procesos protegidos.

**Activación por período (operación manual, fuera de los procesos protegidos):**

```bash
python3 scripts/generar_indice_ofertas_por_proceso.py --periodo 2026-06
python3 scripts/generar_indice_ofertas_por_proceso.py --periodo 2026-07
python3 scripts/generar_indice_ofertas_por_proceso.py --periodo 2026-08
python3 scripts/generar_indice_ofertas_por_proceso.py --periodo 2026-09
# Repetir para cada período adicional publicado, incluido el mes operativo.
```

Luego revisar conteos, tamaño, integridad de los JSON y publicar el directorio generado en GitHub Pages. La búsqueda verifica `version`, mes y `fuente_conteos` contra el catálogo vigente. Si el índice no existe (404), continúa con el método anterior de fragmentos. Si el archivo existe pero está desactualizado o incompleto, falla sin publicar cifras potencialmente incorrectas. El navegador reutiliza archivos ya consultados durante la sesión. **Hasta ejecutar el generador y publicar sus resultados, la mejora estructural de tiempos todavía no está activa para esos meses.** Los índices deben regenerarse cuando se publiquen nuevos registros de ofertas del mes. No se ha conectado este generador a los workflows operativos protegidos.
