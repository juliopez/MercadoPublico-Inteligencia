# Favoritos y exportación CSV — Frontend V2 (21-10-2026)

## Contexto
El usuario validó el autocompletado del comparador y aprobó continuar. Se consultaron README, índice documental, decisiones técnicas, auditoría V1/V2 y frontend actual antes de intervenir.

## Funciones implementadas
- **Favoritos:** botón en cada registro de la tabla cargada. Guarda y elimina entradas usando `localStorage` con clave nueva `observatorio-favoritos-v2`, aislada de V1. Incluye período, entidad, etiqueta y datos públicos. Límite de 200 favoritos en el navegador, sin sincronización con cuenta o Sheets. Panel de favoritos con opción Eliminar.
- **CSV:** botón que descarga los registros filtrados del **bloque actual** (máximo aproximadamente 1.000 filas), no la totalidad del período. Columnas visibles de la entidad, separador punto y coma, UTF-8 BOM, comillas escapadas y neutralización de comienzos de campo asociados a fórmulas.
- No cambia motor de carga, tamaño de los fragmentos, paginación de 10 registros, V1 ni archivos de datos.
- La sección exportada se limita al bloque y a sus filtros locales; no representa búsqueda global ni descarga mensual.

## Verificación
Workflow GitHub Actions [#39667281901](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39667281901), `completed/success`. Se verificó sintaxis Node de `app.js` y existencia de elementos/funciones/límites. **Aún no se comprobó la interacción en navegador** ni la apertura del archivo CSV en Excel/LibreOffice; se requiere validación del usuario.

## Archivos
`frontend-v2/index.html`, `frontend-v2/js/app.js`, `.github/workflows/validar-favoritos-csv-v2.yml`.
