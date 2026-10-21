# Línea base estable del frontend MER v2 — 21 de octubre de 2026

## Alcance y evidencia

La persona usuaria **confirmó en la interfaz** que, después de la última corrección de JavaScript, los datos de todos los períodos y entidades consultables **cargan correctamente** y que la **velocidad de carga es muy buena**. Esta es validación funcional reportada por el usuario, no una medición automática de tiempos. El despliegue correspondiente fue [GitHub Actions #39648640141](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39648640141). Se establece este estado como **línea base funcional a preservar**.

Frontend v1: `index.html` y `data/`, en producción y sin alteraciones intencionales durante el desarrollo v2. Frontend v2: `frontend-v2/index.html`, `frontend-v2/js/app.js`, `frontend-v2/css/styles.css` y `frontend-v2/data/`, ruta independiente `/frontend-v2/`.

## Comportamientos confirmados / implementados

- Selección de períodos 2026-06 a 2026-10 mediante `frontend-v2/data/catalogo-publico.json`.
- Consulta de las cuatro entidades públicas: `procesos`, `ofertas`, `resultados`, `ordenescompra`. Junio–septiembre contienen las cuatro entidades; octubre tiene Ofertas y Resultados sin registros en la exportación observada.
- Fragmentación por período y entidad; se descarga solo el bloque solicitado (aproximadamente 1.000 registros por fragmento), no todos los fragmentos del mes. Reintentos en caso de error y origen alternativo para recuperar un fragmento.
- Presentación paginada en **10 registros por página**, con botones anterior/siguiente, selector de entidad y acción **Ver detalle** con campos públicos del registro. Procesos disponen de enlace al portal oficial.
- La búsqueda textual **se limita al bloque descargado**: no es aún una búsqueda global de todos los registros del período, incluso si el contador muestra el total del catálogo.

## Cobertura histórica comprobada en manifiesto JSON v2

| Mes | Procesos | Ofertas | Resultados | Órdenes de compra |
|---|---:|---:|---:|---:|
| 2026-06 | 80.898 | 407.923 | 63.214 | 150.451 |
| 2026-07 | 80.996 | 437.855 | 54.526 | 150.980 |
| 2026-08 | 83.937 | 432.111 | 65.945 | 153.221 |
| 2026-09 | 79.376 | 398.018 | 48.637 | 147.966 |

**Total de las cuatro entidades publicadas en esos meses:** 2.835.834 registros. Son registros de tablas y meses, no procesos únicos. `Proveedores` y `VinculosCOT_OC` continúan en la base MER v2, pero todavía **no se han integrado funcionalmente** como fichas o relaciones dentro del frontend.

## Incidente y solución que no debe revertirse

La primera estrategia descargaba todos los fragmentos al consultar una entidad: causó fallas de lectura y mal desempeño. Se introdujo lectura por bloque, pero una expresión regular accidental `/^20\\d{2}.../` en `consult()` rechazaba todos los períodos válidos. Se corrigió a la expresión funcional `/^20\d{2}-(0[1-9]|1[0-2])$/`, y se desplegó la versión que el usuario validó.

**No sustituir el mecanismo de carga por una descarga completa de ofertas, ni modificar simultáneamente la navegación y el contrato de datos.** Antes de cambiar JavaScript, asegurar una prueba para selección de período y lectura del primer fragmento de al menos Procesos y Ofertas; verificar cambio de entidad, paginación de 10 y error de fragmento. Mantener posibilidad de revertir el cambio de v2, sin tocar la v1.

## Próxima etapa — recuperar funcionalidades de v1

La prioridad aprobada es el **detalle relacionado de la licitación**. No reemplazar la vista de consulta ni perder búsqueda/paginación actuales. La secuencia de desarrollo debe abarcar:

1. Leer las funcionalidades implementadas realmente en `index.html` v1 (detalle del proceso, ofertas vinculadas, resultados/verificación, OC y enlaces externos), y documentar su contrato real antes de trasladarlas.
2. Resolver relaciones **por código de proceso y período**; evitar confundir igual código de meses distintos. Usar `Proveedores` y `VinculosCOT_OC` como soporte cuando la relación esté comprobada; no inferir adjudicación solo por coincidencia textual o selección.
3. Preparar índices/extractos públicos orientados al detalle para recuperar datos relacionados sin descargar todas las Ofertas de un mes. Restringir columnas públicas y evitar RUT e identificadores internos.
4. Implementar vista de detalle enriquecida con secciones de ofertas, resultados y OC asociadas; estado de verificación y enlaces oficiales, distinguiendo información disponible de no verificada.
5. Recuperar después perfiles de organismo y proveedor, comparación de empresas, favoritos y CSV, validando **cada cambio** contra la v1.

**Criterio de aceptación:** detalle completo de un proceso de ejemplo con relaciones verificadas, navegación intacta para todos los períodos y entidades, paginación 10 y tiempo de carga percibido igual de satisfactorio, sin escritura en Sheets y sin alteraciones de v1. No afirmar esta etapa implementada antes de pruebas.

## Regla de continuidad

Consultar [README principal](../README.md), [decisiones vigentes](DECISIONES_TECNICAS.md), [README v2](../frontend-v2/README.md) y este documento antes de nuevas intervenciones. Este registro sustituye descripciones de estados anteriores que aparecen cronológicamente en el README v2; aquellas se preservan como bitácora.
