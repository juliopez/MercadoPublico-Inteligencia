# Frontend V2 — Guía funcional y estado vigente

**Revisión:** 21-10-2026. **[Abrir V2](https://juliopez.github.io/MercadoPublico-Inteligencia/frontend-v2/)** · [README del proyecto](../README.md) · [Índice documental](../docs/INDICE_DOCUMENTACION.md).

V2 es un **frontend paralelo** que publica extractos autorizados de Mercado Público. V1 continúa operando desde `../index.html`; no se modifica por el desarrollo V2.

## Cómo utilizarlo

1. Seleccionar **mes de referencia y entidad** (Procesos, Ofertas, Resultados u Órdenes de compra).
2. Para explorar rápidamente, pulsar **Mostrar registros del período**: carga el primer bloque (hasta 1.000 registros), presenta páginas de **10** y desplaza a la tabla de resultados. La exploración por bloques y sus filtros locales están en el panel avanzado.
3. Para localizar un código, organismo o proveedor entre los registros de **todo el mes**, utilizar la **búsqueda global indexada**, que comprueba candidatos leyendo únicamente fragmentos necesarios. Puede incluir filtros según entidad. Las sugerencias son ayudas, no listas exhaustivas.
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

**Auditoría de relaciones CA–OC:** [Caso 839-4-COT26](../docs/AUDITORIA_VINCULO_CA_OC_2026-10-21.md). El 60,4 % de OC publicadas carece de `codigo_proceso`; cero enlaces exactos no demuestra que no exista orden de compra. La candidata identificada requiere verificación documental externa.

**Vinculación asistida de OC (nueva):** la pestaña Órdenes de compra separa vínculos exactos por código de **candidatas no verificadas** basadas en misma unidad compradora y proveedor seleccionado. Fuente: índices estáticos `data/oc-candidatas/` de junio–octubre 2026. Ejemplo: `839-4-COT26` y candidata `839-10-AG26`; la coincidencia no demuestra adjudicación ni autoriza completar automáticamente `codigo_proceso`. Véase [auditoría CA–OC](../docs/AUDITORIA_VINCULO_CA_OC_2026-10-21.md).
