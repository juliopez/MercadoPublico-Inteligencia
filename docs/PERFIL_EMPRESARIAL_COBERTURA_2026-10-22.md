# Perfil empresarial — mejora de cobertura 22/10/2026

## Objetivo
Presentar participación histórica y montos ofertados por empresa sin equiparar ofertas a adjudicaciones.

## Ajuste aplicado
Se corrigió el cómputo de procesos distintos por mes en `frontend-v2/js/participantes-historicos.js`: ahora el índice es exigido solo para meses en que la empresa tiene registros. Anteriormente, meses vacíos provocaban el mensaje «En preparación» incluso si los meses activos poseían índices de participación.

Las tarjetas distinguen registros de ofertas, meses de actividad, **monto total ofertado informado**, **procesos distintos dentro de cada mes**, cobertura de ofertas con importe y, con texto explícito, adjudicaciones y montos adjudicados **sin datos suficientes**. Se evita mostrar «0 ganadas» cuando falta evidencia.

## Limitaciones
1. La suma de procesos distintos por mes no deduplica el mismo código entre meses; el contador lo indica.
2. El nombre normalizado no constituye identidad jurídica verificable; falta unificación por RUT.
3. No se infiere una pérdida por ausencia del nombre en Resultados. La selección puede estar pendiente, resultar ambigua o no contar con fuente.
4. Montos ofertados, presupuestos, montos adjudicados y OC son magnitudes distintas.
5. Octubre del MER operativo aún no contiene filas de Ofertas ni Resultados; el perfil depende de meses con cobertura histórica.

## Arquitectura siguiente
Para reportar ganadas/perdidas y sumas adjudicadas confiables se requerirá un índice público derivado de unión por código de proceso + RUT verificado + resultado acreditado y consolidación transversal entre períodos. Debe ser agregado estático precalculado en GitHub Actions, sin consultas masivas desde el navegador ni cambios de infraestructura. Clasificar en adjudicada, no adjudicada con resultado concluyente y sin resolución verificable. La tarea 5 de API Compra Ágil es fuente complementaria futura.

## Validación
Revisar Actions del commit y Pages, consultas de participantes con meses vacíos y no vacíos, cantidad de procesos distintos en los meses activos, sumas monetarias y ayudas. Sin cambios en Sheets, ETL Ubuntu o históricos.

## Corrección funcional del perfil (22/10)
El perfil de proveedor ahora lee también los índices públicos de `resultados` por nombre normalizado en todos los períodos y muestra **Resultados con empresa seleccionada**. Para MULTITODO SPA los índices disponibles registran junio 49, julio 43, agosto 40 y septiembre 40 (172 registros). El contador no se etiqueta «procesos ganados» porque podría haber repeticiones entre períodos y falta verificar cada adjudicación. `Procesos ganados verificados` permanece pendiente y el monto adjudicado no se sustituye por el monto ofertado. Cambio frontend `433c74de`. Verificar despliegue Pages y concordancia de los 172 resultados.

## Consolidación de selecciones entre períodos — 22/10
- `scripts/generar_participacion_historica_v2.py` enriquece los shards públicos de participante con `codigos_seleccionados`, `selecciones_distintas_mes` y `montos_seleccionados_por_codigo`, utilizando exclusivamente Resultados asociados al adjudicatario por nombre normalizado. No asume que la selección representa adjudicación contractual verificada.
- `frontend-v2/js/participantes-historicos.js` une códigos con `Set` entre todos los meses para mostrar **procesos distintos con selección registrada**, y suma una sola vez las ofertas seleccionadas con monto informado cuando los importes por código son consistentes. El conteo histórico de Resultados sigue disponible por separado.
- `publicar-participacion-v2.yml` genera índices al cambiar generador o frontend; `preview-frontend-v2.yml` despliega Pages tras finalizar exitosamente ese workflow sin depender del `push` de un token automático.
- Advertencias: igualdad de nombres no sustituye RUT; un resultado puede ser selección histórica no verificada; sin adjudicación demostrada no afirmar procesos ganados ni monto adjudicado. Si índices no disponibles el indicador declara pendiente en vez de cero.
- Regeneración de todos los meses iniciada en GitHub Actions; pendiente comprobar resultados, coherencia del caso MULTITODO SPA y disponibilidad en Pages. No se cambian ZIP, Google Sheets ni cron diario Ubuntu.

## Indicadores complementarios (22/10)
El perfil incorpora **tasa de selección registrada** = 100 × cantidad de códigos distintos con selección y participación documentada / cantidad de códigos distintos en ofertas de la empresa, deduplicando transversalmente todos los meses publicados. Se calcula **solo** si los nuevos índices incluyen `codigos_participados` en todos los meses con ofertas; de lo contrario no se publica una tasa engañosa. No es tasa de adjudicación efectiva.
También se incorpora **relación monto seleccionado / ofertado** = suma de importes de ofertas seleccionadas con dato conocido / suma de montos ofertados informados. Es una relación de magnitudes, no una tasa contractual y puede tener cobertura incompleta. No reemplaza monto adjudicado.
Los índices agregan `codigos_participados` y mantienen `codigos_seleccionados` para cotejar numerador y denominador. Los scripts existentes de índices se activan por push al cambiar el generador; Pages se publica tras el workflow exitoso. Verificar el caso MULTITODO SPA una vez concluida la regeneración. El cron y la BBDD no se alteraron.

## Incidencia CI de índices de participación — 22/10 noche
Captura del usuario muestra fallos/cancelaciones de Actions. Logs del run `39869752830` identificaron conflictos masivos de `git rebase` al aplicar un commit de fragmentos calculados para 2026-06 sobre nuevos índices ya publicados. La causa fue escribir y confirmar mensualmente, haciendo push/rebase en cada mes con el repositorio en actualización continua. No implica fallo de Google Sheets ni pérdida de los históricos.

Corregido en `5bbff98d` (`.github/workflows/publicar-participacion-v2.yml`): un solo commit atómico para los cinco meses; relectura de `origin/main`, regeneración completa y reintentos mediante restablecimiento del checkout a HEAD de main antes de regenerar. Se eliminó el disparador por cambios únicamente del JS para reducir ejecuciones redundantes; se conserva ejecución manual y cambios del generador. Validación aún pendiente de conclusión del nuevo workflow y de Pages. No tocar cron Ubuntu ni reiniciar ETL para solucionar este incidente.

## Reorganización UX aprobada (22/10)
El frontend agrupa las métricas existentes en tres bloques semánticos: **Participación** (ofertas, meses, procesos, cobertura), **Efectividad** (selecciones registradas, tasa y pendientes de verificación) y **Resultados económicos** (montos ofertados, seleccionados, relación y adjudicados). El párrafo de estado se reduce a resultados encontrados más advertencia general; las definiciones metodológicas de cada tarjeta están centralizadas en `frontend-v2/js/ayudas-contextuales.js` y se activan con el ícono accesible ⓘ. CSS adaptable a desktop y móvil. Los cálculos e índices, el MER operativo, cron Ubuntu y workflows de las 16/17 h no se modifican. Pendiente comprobación visual tras despliegue Pages.

## Auditoría de procesos únicos MULTITODO SPA (22/10, cierre UX)
El usuario cuestionó el indicador 834. Lectura directa de los cuatro shards públicos de participación para `multitodo spa` (`cc.json`): junio 222, julio 202, agosto 208, septiembre 202; unión de `codigos_participados` en todos los meses = **834 códigos distintos**, suma mensual = 834 y duplicados transversales = **0**. Las 845 ofertas no equivalen a 845 procesos porque hay ofertas múltiples en algunos códigos. El dato es correcto para la cobertura actual pero la etiqueta «Procesos distintos por mes» es imprecisa. Cambio `72e6bdcb`: utilizar el tamaño de la unión transversal por código y mostrar «Procesos únicos participados», con control de cobertura de índices; tooltip metodológico modificado en `3bcd2593`. La identidad de la empresa sigue basada en nombre normalizado, no RUT verificado. Pendiente comprobación del despliegue Pages.

## Visualización de distribución aprobada — 22/10 noche
Se reemplazaron las barras horizontales simples del perfil histórico por una visualización SVG circular tipo dona inspirada en el mockup aprobado: distribución porcentual por meses, cifra total central, segmentos en tonos azules, leyenda con mes/cantidad/porcentaje y cuadro explicativo metodológico. El dibujo usa exclusivamente los `rows` ya consultados en los índices JSON y no incorpora dependencias ni llamadas adicionales. Los botones «Examinar AAAA-MM» siguen funcionando. Se adapta a móvil mediante CSS. El cero mensual se muestra en leyenda sin inventar segmento. Se conserva la distinción entre ofertas, procesos únicos y adjudicaciones. Commits `aea54c61`, `4ab96de1`, `7974a942`. Se requiere comprobar visualmente Pages tras su despliegue.
