# Búsqueda histórica transversal de participantes — V2 (21-10-2026)

## Petición y alcance
Se incorporó un acceso directo para buscar **empresas oferentes** y **organismos compradores** en todos los períodos publicados, sin depender de abrir primero una ficha o perfil. Se revisaron README principal, índice, decisiones, manual V2, catálogo y código. V1, MER Sheets, ETL e históricos originales no se modificaron.

## Experiencia de uso
En «Participación histórica de empresas y organismos» se elige el tipo de actor, se introduce el nombre con sugerencias mensuales y se consulta el período histórico completo. Se presentan cantidades de registros, meses con actividad, suma descriptiva de importes y gráfico de evolución mensual. Los botones «Examinar AAAA-MM» trasladan a búsqueda global de la entidad correspondiente para revisar registros y códigos. No se descargan todos los fragmentos históricos en el navegador.

## Indicadores y fuentes
- Los totales mensuales de **ofertas de proveedor** y **procesos publicados por organismo** se obtienen de los perfiles públicos agregados preexistentes (`data/perfiles/<mes>/<entidad>/<sha2>.json`).
- Se añadió `scripts/generar_participacion_historica_v2.py`: calcula para cada proveedor el número de códigos de proceso diferentes entre sus ofertas **de cada mes**, y para cada organismo la cantidad de ofertas vinculadas a sus procesos publicados **en el mismo mes**. Se publican índices por nombre normalizado y sugerencias por prefijo, discriminando proveedor/organismo. No confundir un total por mes sumado entre meses con cardinalidad global deduplicada; un proceso podría aparecer en más de un mes.
- La vinculación de ofertas con organismos requiere coincidencia exacta por código; cuando la fecha del proceso no coincide con el mes de la oferta, esa oferta no se atribuye al organismo por este agregado. Los indicadores se denominan «ofertas recibidas vinculadas» y no «total de ofertas recibidas».
- Las empresas se agrupan por nombre normalizado, **no RUT**. Una variante de razón social puede segmentar la actividad de una misma persona jurídica; también cabe homonimia.
- Los importes son declarados y descriptivos; no equivalen a pagos, contratos definitivos ni adjudicaciones confirmadas.

## Código
- `frontend-v2/index.html` (nueva sección, inputs, resultados, enlaces, sugerencias).
- `frontend-v2/js/participantes-historicos.js` (lectura selectiva mensual, agregados y gráfico).
- `frontend-v2/css/styles.css` (presentación).
- `scripts/generar_participacion_historica_v2.py` y `.github/workflows/publicar-participacion-v2.yml` (generación/publicación).

## Verificación y pendientes
La primera ejecución [#39692345509](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39692345509) falló en `git push` por cambios concurrentes en `main` durante publicación; la generación y la sintaxis pasaron. El workflow tiene reintentos seguros y se activó una segunda ejecución [#39692446114](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39692446114). **No afirmar que los índices están publicados hasta verificar resultado y metadatos para junio–octubre.** Revisión visual y comprobación de participación real de un proveedor y un organismo siguen pendientes. La auditoría integral V2 sigue pendiente como tarea independiente.
