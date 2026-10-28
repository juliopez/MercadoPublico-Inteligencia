# Transformación API → MER sin nuevas consultas — 28/10/2026

## Decisión y evidencia
La ejecución [40787977408](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/40787977408) confirmó HTTP 200, 15 cotizaciones y una seleccionada para `839-4-COT26`, pero **no archivó el JSON original**. No es posible transformar esas 15 filas ahora: los logs solo contienen banderas de presencia y conteos. No volver a consultar ChileCompra para esta fase.

## Implementación
- `scripts/adaptar_detalle_compra_agil_mer.py`: adaptador puro de un JSON de detalle V2 a las cabeceras reales de las tablas MER **Ofertas (9)** y **Resultados (10)**.
- `tests/test_adaptar_detalle_compra_agil_mer.py`: pruebas offline con datos sintéticos (no representan las cotizaciones reales de la API).
- Sin dependencias HTTP, sin credenciales y sin escrituras Sheets. El módulo lee por stdin cuando se usa como CLI.
- Clave Ofertas `(codigo,id_cotizacion)`; `id_proveedor` queda vacío hasta resolver identidad en Proveedores. `rut_proveedor_cot` se conserva para conciliación privada.
- Solo se crea Resultados cuando el JSON indica exactamente una cotización seleccionada; nunca se genera adjudicatario, adjudicación ni OC pública desde esa selección.
- Los campos denominados `*_clp` quedan vacíos por defecto hasta verificar documentalmente moneda; solo se incluyen al activar explícitamente `clp_verificado=True` tras la validación.
- Se rechazan cotizaciones duplicadas, identificadores vacíos, payload inválido y selecciones múltiples ambiguas. Ausencia de lista de cotizaciones produce error; lista vacía informada sí es válida.

## Limitaciones antes de producción
1. Falta capturar un JSON real de API como artefacto temporal privado, sin subir respuestas crudas al repositorio ni a Pages; sería necesaria una **nueva consulta** en una ejecución posterior, **no realizada en esta intervención**. Alternativamente transformar cualquier JSON ya conservado legítimamente en un respaldo local.
2. No hay conciliador `id_proveedor` conectado al adaptador.
3. No hay proceso de upsert ni checkpoints habilitados contra las seis hojas reales.
4. Esta implementación no incorpora la API V1 de adjudicaciones.
5. Los tests son offline con fixtures inventados y NO equivalen a una transformación validada con las 15 ofertas reales.

## Pruebas y comando sin API
`python -m unittest discover -s tests -p 'test_adaptar_detalle_compra_agil_mer.py'`

Para transformar un JSON local ya almacenado:
`python scripts/adaptar_detalle_compra_agil_mer.py < detalle_v2.json`
No emplear `--clp-verificado` hasta acreditar que `monto_total` está expresado en CLP.
