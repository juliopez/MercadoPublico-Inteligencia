# Analítica interactiva y relaciones históricas multimes — frontend V2

**Fecha:** 21-10-2026. El usuario autorizó realizar en una intervención las tres mejoras al panel mensual (selección de mes, comparación y perspectivas) y ampliar las fichas para buscar en **todos los archivos históricos publicados**.

## Alcance y documentación
Se consultaron antes de editar README, índice documental, decisiones técnicas, catálogo público y código vigente de frontend-v2. **Cobertura actual del catálogo: junio–octubre de 2026**, no la totalidad de ChileCompra ni meses no publicados. No se modificó V1, Google Sheets, ETL ni fragmentos originales.

## Panel interactivo
- Al seleccionar una barra mensual se actualiza el período de análisis y se puede navegar directamente a sus registros.
- El selector «Comparar con» incorpora otro mes y compara totales y diferencias porcentuales; octubre de 2026 está incompleto.
- El selector «Perspectiva» permite tres vistas: Actividad, Organismos o proveedores (ranking por número de registros) y Montos registrados (sumas CLP y cobertura de registros con monto).
- Un proceso externo crea un JSON agregado por período y entidad, por lo que el navegador solo descarga archivos pequeños. Script `scripts/generar_analitica_v2.py`, workflow `.github/workflows/generar-analitica-v2.yml`.
- **18 agregados publicados** y reconciliados contra el catálogo. Workflow de generación [#39681745265](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39681745265), `success`; se verificaron manualmente los 18 JSON y sus conteos. Los resultados de montos no acreditan pagos o adjudicaciones definitivas; si no existe monto informado se indica expresamente.

## Relaciones entre archivos históricos
- Las fichas de Procesos, Ofertas, Resultados y Órdenes de compra pueden consultar su código de proceso (campo `codigo_proceso` para OC y `codigo` para las otras entidades).
- La consulta inspecciona los cinco índices históricos `data/indices/AAAA-MM.json` para Ofertas, Resultados y OC, y solo descarga fragmentos de los códigos relacionados. No se limita al mes de la ficha.
- Al verificarse los índices se detectó que **no incluían Procesos**. Se generaron índices exactos complementarios `data/relaciones-procesos/AAAA-MM/hash.json`, con coordenadas [fragmento,fila] para localizar la ficha del proceso también desde una OC. El generador es `scripts/indexar_relaciones_procesos_v2.py` y el workflow de publicación `.github/workflows/publicar-relaciones-procesos-v2.yml`.
- Los cinco metadatos de Procesos fueron consultados y conciliados: junio 80.898, julio 80.996, agosto 83.937, septiembre 79.376 y octubre 1.558. La ejecución de publicación [#39682406233](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39682406233) concluyó `success`.
- La sección de detalle presenta cuatro grupos: Procesos, Ofertas, Resultados y Órdenes de compra; cada fila incluye el mes de procedencia. Las tablas tienen deslizamiento horizontal propio y diseño de dos columnas en escritorio, una en móvil.
- Cuando un índice o fragmento no esté disponible se presenta advertencia de **cobertura parcial** en vez de afirmar que no existen registros. Un código sin relación no prueba que no hubo contratación.

## Verificación
Workflow `.github/workflows/validar-analitica-historicos-v2.yml`: sintaxis JavaScript, controles del panel, integración de las relaciones y apertura válida de los índices de los cinco períodos. Pruebas automatizadas aprobadas [#39682595022](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39682595022). La última actualización a todas las entidades desencadenó una nueva ejecución; consultar estado para validar esa revisión final.

**Pendiente:** prueba interactiva en navegador de las tres vistas, selección/comparación y fichas con relaciones que efectivamente abarcan meses distintos; medir tiempo de carga en escenarios de códigos con muchas relaciones. La auditoría integral independiente sigue pendiente.
