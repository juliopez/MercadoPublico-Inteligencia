# Ajustes UX frontend V2 — 22/10/2026

## Objetivo
Priorizar localización transversal de procesos, OC, proveedores y organismos; reducir pasos y simplificar navegación sin modificar contratos de datos, ETL, cron ni hojas MER.

## Cambios implementados
1. Se posicionó la sección `#busqueda-global` antes de la consulta por período. Es ahora el primer bloque funcional tras la navegación.
2. La navegación principal se simplificó a cinco accesos: Buscar, Explorar por período, Analizar, Participantes y Seguimiento. Todas las secciones funcionales originales permanecen accesibles mediante desplazamiento.
3. Se trasladó el **único** selector `#entidad` al formulario de búsqueda global, manteniendo su mismo identificador y el consumo de estado por los módulos JavaScript existentes.
4. La consulta por período queda como exploración secundaria, con filtros locales avanzados preservados.
5. Se aclaran títulos, textos de ayuda y jerarquía visual, incluido diseño adaptativo móvil.
6. La ficha de detalle, scripts de búsqueda, índices, datos públicos y relaciones permanecen intactos: no se cambia semántica ni disponibilidad.

## Evidencia verificable
- Identificadores `entidad`, `periodo`, `busqueda-global`, `busqueda-global-texto`, `consulta`, `resultados` y `detalle`: una sola ocurrencia cada uno en el HTML.
- Orden DOM: búsqueda transversal → exploración por período → analítica.
- Cambios confinados a `frontend-v2/index.html` y `frontend-v2/css/styles.css`.
- Estado: **implementado en main**, sin afirmar aún validación visual en GitHub Pages ni ejecución de todas las interacciones en navegador.
- Revisar específicamente navegación desde `#participantes-historicos` hacia búsqueda global, «Ver detalle» y retorno al contexto; también comprobar que la entidad elegida se comparte entre los módulos.

## Próxima validación
Tras los trabajos automáticos de las 16:00 y 17:00, verificar que Pages sirva la nueva jerarquía, que «Buscar» funcione sin elegir previamente período cuando cobertura es «Todos», que la consulta por período siga disponible y que no existan errores de consola. Si algún test falla, revertir solo los commits UX; nunca reprocesar Sheets.
