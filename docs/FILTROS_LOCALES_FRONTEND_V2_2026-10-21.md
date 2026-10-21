# Filtros locales de frontend V2 — 21-10-2026

## Consulta documental
Se revisaron README, índice documental, decisiones técnicas, documentación de la mejora de tablas y código vigente HTML/JS/CSS de frontend-v2. Se respetó la regla de documentar después de implementar.

## Cambios realizados
- HTML: controles de Estado o selección, Modalidad o tipo y Limpiar filtros, con advertencia de alcance restringido al bloque descargado.
- JS: filtros por `estado` y `modalidad` para Procesos; `seleccionado` para Ofertas; `validado` para Resultados; `estado` y `tipo_oc` para Órdenes de compra.
- Los valores de listas se derivan de registros del bloque visible; se desactiva el selector no aplicable.
- La paginación usa los mismos resultados filtrados y conserva 10 filas por página. Se actualizaron opciones al cambiar de bloque, período o entidad.
- CSS: presentación adaptable de los filtros y botón de limpieza.
- Sin modificación del lector de fragmentos, catálogo público, datos, ETL, Sheets ni frontend V1.

## Validación y límites
Comprobación estática posterior a commits: controles, funciones, CSS, lógica de paginación y funciones de lectura por bloque presentes; no queda el conteo anterior de paginación sin aplicar filtros. Falta prueba real de navegador y despliegue. **Los filtros no buscan en el mes entero.**

## Commits
`8e1d565d` (HTML), `cbabfb90` (JS), `b4b9fafa` (CSS).

## Siguiente trabajo
Verificar interacciones en navegador y después diseñar búsqueda indexada global si se requiere recuperar toda la búsqueda de V1, preservando la carga por fragmentos.
