# Mejora de tabla principal frontend V2 — 21-10-2026

## Propósito
Recuperar claridad de lectura de las tablas V1 sin alterar consulta por fragmentos de V2.

## Consulta previa
Se revisaron README, índice documental, decisiones técnicas, mejora visual anterior, código de V1, `frontend-v2/js/app.js`, CSS vigente, manifiesto público y ejemplos reales del primer fragmento de Procesos, Ofertas, Resultados y Órdenes de Compra de junio de 2026.

## Implementación
- `frontend-v2/js/app.js`: cuatro configuraciones explícitas de columnas, con etiquetas legibles y distinto orden por entidad. Se eliminó el corte de 16 columnas siguiendo el orden arbitrario del JSON en el listado; la ficha «Ver detalle» sigue mostrando el registro.
- Procesos: código, nombre, modalidad, organismo, estado, publicación, cierre y monto disponible.
- Ofertas: código, proveedor, monto ofertado, selección y fecha.
- Resultados: código, proveedor informado, monto adjudicado, monto de oferta seleccionada, validación y verificación OC; etiquetas deliberadamente diferentes para no equiparar selección a adjudicación.
- Órdenes: código OC, proceso asociado, proveedor, estado, monto y creación.
- Formato de montos CLP sin decimales, conservando «No informado» cuando faltan datos. Código y nombre destacados; estados con etiqueta neutra. Contador precisa que los resultados corresponden al bloque cargado.
- `frontend-v2/css/styles.css`: scroll horizontal, jerarquía tipográfica, montos alineados y resaltado de filas.
- Sin cambios en carga por bloques, caché, reintentos, catálogo, índices, datos, Sheets, ETL o V1.

## Evidencia de revisión
Commits código `16a25b1c` y estilos `5a0ae62d`. Se comprobaron estáticamente las cuatro configuraciones, paginación de 10, presencia de `loadChunk` y `loadRelated`, desaparición del corte de 16 columnas, formateo de montos y estilos. No se realizó prueba funcional de navegador ni medición de rendimiento; publicación vía Pages aún requiere comprobación.

## Pendientes
Validar visualmente y en navegador los cuatro tipos de entidad, desplazamiento horizontal, acción Ver detalle y navegación entre bloques. Después recuperar progresivamente filtros de V1, siempre con índices cuando se requiera cobertura global.
