# Auditoría funcional V1 → V2 — 21-10-2026

## Protocolo de intervención aprobado
Antes de toda acción, revisar `README.md`, `docs/INDICE_DOCUMENTACION.md`, `docs/DECISIONES_TECNICAS.md`, la documentación específica y el código vigente. Después de implementar, registrar cambios, archivos, verificaciones, resultado y pendientes. No confundir código implementado, CI exitosa y validación real de navegador.

## Fuentes de esta auditoría
Se leyeron README principal, índice, decisiones técnicas, línea base V2 y el código `index.html` (V1), `frontend-v2/index.html` y `frontend-v2/js/app.js`. Se contrastó además el inventario y bitácora de `frontend-v2/README.md` y las relaciones descritas en `docs/DETALLE_RELACIONADO_FRONTEND_V2.md`.

## Diagnóstico comprobado en código
| Capacidad | V1: implementación identificada | V2: implementación identificada | Decisión |
|---|---|---|---|
| Carga | `data/observatorio.json`, colecciones/indexación en memoria; CSV manual complementario | Catálogo por mes y entidad, fragmentos JSON bajo demanda con reintentos y origen alterno | **Conservar V2**; no replicar carga global V1 |
| Búsqueda | Global con sugerencias para proceso, empresa y organismo; búsqueda de procesos | Búsqueda textual en `state.records` (fragmento cargado) | Diseñar índice global progresivo sin descargar entidad completa |
| Filtros | Código/nombre, empresa, participación, fecha, situación, modalidad, categoría, región, organismo | Período, entidad, texto local al fragmento | Trasladar controles gradualmente; diseñar consultas indexadas |
| Detalle | Ficha con fuentes, ofertas y resultados; perfiles complementarios | Ficha básica, portal oficial y secciones relacionadas de ofertas/resultados/OC cargadas por índice y código/período | Mejorar presentación V2 y probar relaciones en navegador |
| Perfiles | `buyerProfile()` y datos de proveedores | Pendientes | Requieren índices públicos seguros por período |
| Comparación | `compareCompanies()`, hasta tres empresas | Pendiente | Implementar sobre agregados públicos, no sobre ofertas completas |
| Favoritos | `localStorage`, clave `observatorio-favoritos-v1` | Pendiente | Evaluar compatibilidad de formato e identificación por período |
| Exportación | Función documentada en inventario V1; validar recorrido real del botón | Pendiente | Exportar únicamente el alcance consultado o definir exportación servidor/archivo |
| Paginación | Paginación en memoria de resultados filtrados | 10 filas por página del fragmento seleccionado | Conservar V2; distinguir página del fragmento de cobertura mensual |
| Indicadores | Indicadores, cobertura y fecha de actualización | Tres tarjetas: período, registros disponibles y fecha de publicación | Ampliar V2 desde metadatos del catálogo |

## Restricciones y riesgos
1. Preservar absolutamente el comportamiento validado de carga por fragmento (~1.000 registros), navegación por período/entidad y paginación de 10, así como el aislamiento de `index.html` y `data/` de V1.
2. La búsqueda local de V2 NO cubre todos los registros aunque el contador sea mensual: no anunciar cobertura global sin índices y prueba.
3. La asociación por código/período no prueba adjudicación. No exponer identificadores internos ni datos privados de Sheets.
4. La implementación de índices de relaciones está documentada, pero la validación funcional del detalle en navegador sigue pendiente.
5. Cambiar una capacidad por vez, con prueba regresiva de Procesos y Ofertas, paginación, error/reintento y detalle. No modificar ETL, hojas, historial ni despliegue principal para mejorar interfaz.

## Orden sugerido para siguientes intervenciones
1. Validar visualmente y mediante pruebas el detalle relacionado ya codificado en V2; corregir solo defectos comprobados.
2. Reorganizar interfaz V2 para recuperar navegación, filtros y presentación de V1 sin alterar `getPart()`, `loadChunk()` o contrato público.
3. Añadir índice de búsqueda mensual global y nuevos filtros, con pruebas de cobertura y tiempos.
4. Añadir perfiles, comparación, favoritos y exportación, uno a uno, sobre índices/agregados seguros.

## Resultado de esta tarea
**Efectuado:** auditoría estática del código y documentación y registro de hallazgos. **No efectuado:** cambios al frontend, Google Sheets, ETL, datos o publicación; tampoco prueba de navegación real. Este documento es una auditoría y no una declaración de funcionalidades nuevas desplegadas.
