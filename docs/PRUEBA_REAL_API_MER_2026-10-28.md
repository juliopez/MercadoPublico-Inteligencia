# Primera prueba real de API — 28 de octubre de 2026

**Estado:** ejecutada en GitHub Actions, solo lectura. [Run 40787977408](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/40787977408), ejecución `success`. Cliente `scripts/probar_campos_api_mer.py`, workflow `.github/workflows/probar-campos-api-mer.yml`; ticket tomado de secreto, no se imprimen datos individuales ni RUT.

## Compra Ágil V2: `839-4-COT26`
- HTTP 200.
- Respuesta raíz con `payload` válido y código coincidente.
- `proveedores_cotizando`: lista con **15** cotizaciones.
- Se informa **1** cotización con `proveedor_seleccionado` verdadero.
- Campos presentes en al menos una oferta: `id_cotizacion`, `razon_social`, `monto_total`, `fecha_creacion`, `proveedor_seleccionado`, `rut_proveedor`: **todos verdaderos**.
- En la oferta seleccionada se encuentran `id_cotizacion` y `monto_total`, mapeables condicionalmente a `Resultados.id_cotizacion_ganadora` y `Resultados.monto_oferta_seleccionada_clp`.
- No se comprobó la moneda de `monto_total` ni la identidad canónica `id_proveedor`, ni que una oferta seleccionada equivalga a adjudicación contractual. Estos son requisitos antes de escrituras.

## Licitación V1: `1000-24-LE26`
- HTTP 200.
- `match_found=false` bajo comprobación de `CodigoExterno` coincidente y objeto `Adjudicacion` tipo diccionario.
- No se pudo confirmar adjudicatario, monto adjudicado ni fecha para esta muestra. Este resultado **no equivale** a negar que existan adjudicaciones en la API; cambiar muestra por una licitación oficialmente adjudicada y verificar estructura de respuesta en un sondeo adicional.

## Inferencias y límites
- Las seis columnas de Ofertas provenientes del detalle V2 ya se observaron en una muestra; los otros tres campos de Ofertas son enlace/identidad interna/fuente y deben calcularse o asignarse conforme al MER.
- La prueba observó la *presencia* de campos y el número de ofertas, no inspeccionó la totalidad de valores ni confirmó unidades monetarias.
- Para Resultados solo se acredita una selección y monto asociado, no una adjudicación ni OC verificada.
- No se escribieron registros ni se alteró el cron. Antes de la carga: adaptadores al esquema real 9/10 columnas, claves y checkpoint externo a las seis tablas.

## Próximo paso
Aislar una segunda muestra de licitación adjudicada, verificar payload y semántica; adaptar el mapper de Compra Ágil al MER y ejecutar pruebas offline/solo lectura que produzcan conteos y planes de inserción/actualización, sin persistir valores reales hasta validación.
