# Panel analítico visual V2 — implementación del primer mockup (22/10/2026)

## Alcance
Se incorpora `frontend-v2/js/analitica-visual.js` al bloque «Evolución mensual de registros», con tres tarjetas visuales: **Montos registrados**, **Organismos compradores / Participantes**, **Actividad mensual**. Diseño adaptativo de tres a una columna y barras seleccionables por mes. El módulo consume únicamente `frontend-v2/data/catalogo-publico.json` y los agregados existentes `data/analitica/AAAA-MM/entidad.json`. No lee Google Sheets, ZIP ni API y no afecta el cron.

## Contrato realmente disponible
Los agregados actuales proporcionan `registros`, `monto_total_clp`, `registros_con_monto`, `actores_distintos_por_nombre` y `top_actores`. **No incluyen** desglose de montos por organismo, actividad diaria ni distribución de registros por categoría. Por esa razón, esta primera implementación muestra ranking de actores **por cantidad de registros**, actividad **por mes** y montos **por mes**; no simula un mapa de calor diario, treemap monetario o gráfico apilado sin respaldo. Octubre se rotula período parcial. Se conserva el bloque analítico previo como referencia funcional y comparador.

## Verificación pendiente
- Comprobar ejecución del validador frontend y posterior despliegue Pages.
- Verificar en navegador las tres tarjetas con Procesos y Órdenes de compra, navegación al seleccionar mes, consistencia de los valores y diseño responsive.
- Comprobar mensajes ante meses sin agregados.
- La comparación intermensual del bloque previo permanece disponible; no atribuir los nuevos gráficos a compras o pagos únicos.

## Iteración futura
Si se aprueba ampliar el generador `scripts/generar_analitica_v2.py`, se pueden incorporar agregados diarios y montos por organismo. Requiere validar cobertura de fechas y exactitud de nombre/identificador; no inventar indicadores.

## Segunda iteración técnica (22/10, pendiente de regeneración)
El generador `scripts/generar_analitica_v2.py` añade `top_actores_monto` (sumas por nombre de organismo o participante) y `modalidades` (conteos por modalidad/tipo). Ambos se derivan EXCLUSIVAMENTE de los fragmentos públicos, sin intervenir Sheets o ZIP. `analitica-visual.js` detecta estos campos de manera opcional: usa ranking monetario si existe y, si no, mantiene el ranking de registros anterior; muestra el desglose de modalidades solo cuando está presente. Los archivos JSON analíticos históricos existentes siguen en versión 1 y **no se han regenerado**. Por tanto, aún no es correcto declarar visible el nuevo ranking monetario ni el desglose de modalidades en producción.

**Pendiente**: pruebas de sintaxis y consistencia del generador; regeneración selectiva con respaldo y comparación de totales; despliegue y prueba visual. No hacer estas operaciones durante el ciclo del ETL 16:00/17:00. La agrupación es por nombre publicado y las modalidades pueden tener valores heterogéneos; no interpretarlas como categorías oficiales homogéneas sin homologación.


## Tercera iteración visual: reproducción progresiva del mockup (22/10)
- Gráfico SVG de tendencia de montos por período, con escala y puntos mensuales derivados de agregados publicados.
- Organismos con ranking compacto, porcentaje real de los tres primeros y dona de concentración **solo** si existen `top_actores_monto`. De lo contrario se conserva ranking por cantidad y se omite la dona (sin porcentajes monetarios inventados).
- Actividad mediante columnas mensuales y porcentajes de variación calculados a partir de conteos publicados. Las modalidades del mes aparecen únicamente con `modalidades`; no se inventan segmentos mensuales hasta disponer del desglose completo por mes.
- Selección de mes desde barras o columnas; nombres largos resumidos visualmente con su nombre completo en atributo `title`.
- No se han modificado fuentes históricas, hojas operativas ni el cron. Los agregados monetarios y de modalidades para los meses antiguos requieren una regeneración pública separada y verificada.
- **Estado de evidencia:** implementación en GitHub; pendiente revisión visual en Pages, sintaxis de módulo nuevo y regresiones funcionales. La aprobación de un mockup no acredita ejecución correcta del frontend.


## Consolidación UX aprobada (22/10): reemplazo del bloque legado
La versión unificada deja visibles solamente tres tarjetas de Montos, Organismos y Actividad, sus visualizaciones y una comparación opcional. Se retira de la página el módulo legado `analitica-interactiva.js` para eliminar el ranking duplicado; se conservan los nodos ocultos `evolucion-resumen`, `evolucion-barras` y `analitica-detalle` porque el controlador principal utiliza algunos para su contrato de datos y eventos. La selección «Perspectiva» destaca una tarjeta y «Comparar con» muestra registros y montos de los dos meses seleccionados; la selección de mes desde las columnas conserva el período visible. Se impide mostrar la variación del mes actual como una caída intermensual comparable.

**Alcance de entrega:** HTML, JavaScript y CSS de V2; no se tocaron históricos, hojas MER ni la programación Ubuntu. Los nuevos agregados `top_actores_monto` y `modalidades` necesitan publicación real para desplegar dona monetaria y desgloses de modalidad. No declarar completa la reproducción del mockup antes de regenerar esos JSON y probar Pages.

**Prueba de regresión necesaria:** entrada y cambio de entidad; selección de perspectiva; comparación intermensual; cambio de mes; acceso a registros del mes; mostrar/ocultar datos faltantes; meses sin desglose monetario; métricas correctas al distinguir octubre parcial. Verificar despliegue por commit, no por presencia del archivo local.

## Ajustes de indicadores y regresión (22/10)
- Importes formateados en CLP completo o expresados en millones/mil millones sin abreviatura ambigua «mil MM».
- Gráfico de montos excluye del trazado los períodos sin montos informados; evita inventar una caída a cero.
- Mes operativo parcial identificado usando año/mes de Chile con `Intl.DateTimeFormat(...).formatToParts`, sin depender de interpretación local de una cadena de fecha.
- Variaciones del mes parcial se rotulan «Parcial»; las comparaciones que lo incluyen no calculan una diferencia porcentual ordinaria.
- Se actualizaron las pruebas estructurales de analítica/UX que aún exigían los textos y el módulo legado eliminado; **pendiente comprobar su ejecución exitosa en Actions**.
- **Pendiente crítico:** regeneración y publicación de los agregados analíticos históricos `top_actores_monto` y `modalidades`; los históricos JSON siguen sin esas claves hasta ejecutar `generar-analitica-v2.yml`. Este paso solo transforma los fragmentos públicos en JSON derivados, pero debe ejecutarse separadamente y validarse. No se ha autorizado una alteración de Google Sheets ni del cron.
