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
