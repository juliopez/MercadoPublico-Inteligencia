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
