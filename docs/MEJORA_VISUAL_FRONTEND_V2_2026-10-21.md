# Mejora visual V1 → V2 — navegación y cobertura (21-10-2026)

## Propósito
Iniciar la recuperación de los elementos de experiencia de usuario de V1 sin modificar el mecanismo de carga selectiva de V2.

## Consulta previa obligatoria
Se revisaron README.md, docs/INDICE_DOCUMENTACION.md, docs/DECISIONES_TECNICAS.md, docs/AUDITORIA_FRONTEND_V1_V2_2026-10-21.md, index.html de V1, frontend-v2/index.html y frontend-v2/css/styles.css.

## Cambios implementados
- `frontend-v2/index.html`: menú de navegación a Consulta, Indicadores y Resultados; identificadores de secciones; ayudas explicativas en indicadores de cantidad y fecha; texto visible que aclara la búsqueda limitada al bloque descargado.
- `frontend-v2/css/styles.css`: estilos de navegación rápida inspirados en V1, foco accesible, diseño responsive y respeto a preferencia de movimiento reducido.
- Se descartó un vínculo al detalle mientras su sección está oculta; las fichas siguen abriéndose con Ver detalle.
- No se modificaron `frontend-v2/js/app.js`, los JSON públicos, el catálogo, los índices, la V1, los ETL ni Google Sheets.

## Validación
Comprobación estática de que los tres enlaces corresponden a identificadores reales, las ayudas y estilos existen y el menú no apunta al detalle oculto. No se ha ejecutado prueba interactiva de navegador ni medido velocidad. Los commits son bce7b7e, 6e4369c y ba079d0.

## Pendientes
Comprobar visualmente en GitHub Pages la adaptación a escritorio/móvil, navegación por anclas y continuidad de consulta por períodos; luego evaluar la siguiente mejora de la interfaz de tablas y filtros. No equiparar la publicación del código a validación en navegador.
