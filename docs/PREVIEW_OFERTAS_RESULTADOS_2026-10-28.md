# Etapa 2 — Prueba de exportación aislada de Ofertas y Resultados (28/10/2026)

## Estado
Se agregó un exportador en modo **preview** que no consulta API, no lee ni modifica Google Sheets y **no escribe en frontend-v2/data**. Las tablas de entrada son matrices JSON con cabeceras reales del MER; se contrastan contra `SCHEMA` de `scripts/importador_historicos_v2.py`.

## Implementación
- `scripts/exportar_ofertas_resultados_preview.py`: emite `partes/ofertas/<periodo>/NNNN.json`, `partes/resultados/<periodo>/NNNN.json` y `manifest.json` con conteos y referencias de catálogo previstas.
- Cada parte contiene a lo sumo 1000 registros; orden estable por proceso e ID de cotización. Se rechazan claves vacías/duplicadas, cabeceras incompatibles y destinos no vacíos.
- Campos públicos elegidos inicialmente para Ofertas: `id_cotizacion,codigo,proveedor,monto_ofertado_clp,fecha_oferta,seleccionado`.
- Campos públicos elegidos inicialmente para Resultados: `codigo,id_cotizacion_ganadora,adjudicatario,monto_adjudicado_clp,fecha_resultado,motivo_seleccion,validado,monto_oferta_seleccionada_clp,estado_verificacion_oc`.
- Se excluyen `id_proveedor`, RUT del proveedor, `fuente` y otros metadatos internos de la salida pública.
- `tests/test_exportar_ofertas_resultados_preview.py`: fixtures sintéticos para validar recuentos, exclusión de datos privados y rechazo de duplicados.

## Límites
1. **No es un publicador activo**. El orquestador y el publicador de Ubuntu siguen exportando únicamente Procesos y Órdenes de Compra.
2. Todavía no se ha conectado un escritor idempotente real para Ofertas/Resultados; el planificador sólo propone cambios.
3. Una ejecución real requerirá snapshot/backup, lock compartido, prueba de escritura y lectura posterior, y decisión explícita para incorporar los dos tipos al publicador existente.
4. Los campos públicos se deben contrastar con el consumidor actual del frontend, antes de reemplazar el catálogo. Los ceros existentes de Ofertas y Resultados siguen describiendo cobertura no publicada.
5. No se ha realizado ninguna solicitud nueva a la API ChileCompra.

## Siguiente paso seguro
Validar localmente preview y planificador con un JSON sintético compuesto, luego preparar escritor con `--simular` predeterminado y `--aplicar` protegido, y prueba aislada de exportación end-to-end contra un libro de prueba/copia; finalmente ampliar producción sin interrumpir el cron.
