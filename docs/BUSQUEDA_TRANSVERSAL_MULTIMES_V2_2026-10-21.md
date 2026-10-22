# Búsqueda transversal multimes — Frontend V2

**Estado:** código implementado y publicado en `main`; comprobación sintáctica del módulo aprobada; revisión visual en GitHub Pages pendiente.

## Problema resuelto

La búsqueda global indexada exigía seleccionar previamente un mes en la grilla principal. Se agregó **Cobertura** con valor inicial `Todos los períodos publicados` y alternativa `Solo período seleccionado`. La elección no afecta la exploración por bloques.

## Implementación

- `frontend-v2/index.html`: selector `busqueda-global-alcance`, título general y botón «Buscar».
- `frontend-v2/js/busqueda-global.js`: reutiliza índices `data/busqueda/AAAA-MM/ENTIDAD` de cada período del catálogo; cruza referencias por término, lee únicamente fragmentos seleccionados y pagina en grupos de 10. Añade columna **Período** a resultados multimes y a CSV.
- Navegación `Ver detalle` usa el mes real de cada fila, no el mes del selector superior.
- `frontend-v2/js/participantes-historicos.js`: los botones «Examinar AAAA-MM» preservan su comportamiento anterior usando alcance mensual.
- No requiere regenerar índices, descargar todos los históricos al navegador ni modificar Google Sheets, ETL, cron o V1.

## Límites y validación pendiente

Resultados corresponden a coincidencias verificadas por fragmento; la paginación comprueba referencias progresivamente. Un mismo proceso en distintos meses se muestra como registros de períodos distintos, no se deduplica indiscriminadamente. La búsqueda sigue requiriendo palabras de tres o más caracteres (salvo código completo). Los períodos parciales solo incluyen fuentes publicadas.

**Revisión visual pendiente:** buscar código `1028871-59-COT26` en «Todos los períodos» y verificar que aparezca `2026-06`; buscar un proveedor frecuente y navegar a resultados de varios meses; cambiar a «Solo período seleccionado» y verificar que desaparezcan coincidencias de otros meses; usar un botón «Examinar» de participantes históricos para confirmar que dirige a la búsqueda mensual; comprobar CSV con columna período y «Ver detalle» al mes correcto.

No declarar GitHub Pages comprobado ni prueba de navegador aprobada a partir de la publicación de código.

## Corrección de «Ver detalle» en resultados multimes

**Incidencia detectada visualmente por el usuario:** la búsqueda transversal recuperaba correctamente registros de otros meses, pero «Ver detalle» no abría la ficha. Causa identificada en `frontend-v2/js/app.js`: `window.openIndexedRecord(part,row,period,entity)` rechazaba registros cuando el mes/entidad del resultado difería de los selectores principales.

**Solución:** usar el `period` y `entity` reales de la fila indexada; validar la ruta contra el catálogo público, sincronizar selectores y estado de bloques, descargar exclusivamente el fragmento indicado y abrir `showDetail`. El botón lleva a la ficha abierta. No cambia la búsqueda, el índice, los datos originales ni el funcionamiento de V1. Sintaxis JS verificada por compilación de la fuente descargada desde GitHub. **Queda pendiente la revisión visual del clic en Pages**, así como descartar regresiones de navegación entre períodos.

Commit correctivo: `b60ee8f`.
