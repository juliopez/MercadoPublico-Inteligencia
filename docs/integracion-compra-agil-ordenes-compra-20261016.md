# Integración Compra Ágil y órdenes de compra — decisión de implementación (16-10-2026)

## Estado inspeccionado
Libro: Observatorio Mercado Público — Base de Datos (ID `1y81QaPy37APkBwxlYrKyE66_1ECdhL87GyWNitTfHr4`).
Pestañas: Procesos, Ofertas, Resultados, Control, Indicadores.
- Procesos: 16 cabeceras reales: `codigo,nombre,estado,convocatoria,fecha_publicacion,fecha_cierre,monto_disponible_clp,organismo_comprador,region,total_ofertas_recibidas,motivo_seleccion,url_detalle,fecha_sincronizacion,categoria,subcategoria,modalidad`. Filas consultadas: modalidad Licitación.
- Ofertas: 7 cabeceras reales: `codigo,proveedor,monto_ofertado_clp,fecha_oferta,fuente,id_cotizacion,seleccionado`. Hay registros históricos de licitaciones.
- Resultados: 10 cabeceras reales: `codigo,adjudicatario,monto_adjudicado_clp,fecha_resultado,motivo_seleccion,fuente,validado,id_cotizacion_ganadora,monto_oferta_seleccionada_clp,estado_verificacion_oc`. Hay registros históricos.
- No existe pestaña ÓrdenesCompra.
- `scripts/sync_chilecompra_sheets.py` ya soporta `SYNC_MODALIDAD=licitaciones|compra_agil`, y proyecta por nombre sobre cabeceras reducidas. No reescribirlo sin necesidad.
- `scripts/etl_multiproceso_manual.py` consulta los códigos `-COTxx` previamente existentes en Procesos y llena Ofertas/Resultados para Compra Ágil; no descubre procesos.
- `.github/workflows/incremental-diario.yml` permanece sin `schedule`, usa 4 ejecuciones por modalidad. **Contrato aprobado: máximo 3 intentos, errores persistentes registrados y reintento el siguiente día.** Corregir cuando se modifique el orquestador; nunca habilitar programación antes de validar cobertura.
- `scripts/diagnostico_ordenes_compra.py` y `scripts/validar_ordenes_ag.py` son diagnósticos, NO ETL operativo. No ejecutarlos para investigar enlaces PDF.

## Modelo objetivo
1. `Procesos`: conservar las 16 columnas actuales y clave `codigo`. Modalidad `Licitación` o `Compra Ágil` según dato oficial.
2. `Ofertas`: conservar cabeceras y usar clave compuesta `(codigo,id_cotizacion)` cuando existe una cotización oficial. No inventar identificadores de ofertas históricas de licitaciones.
3. `Resultados`: conservar selección de Compra Ágil diferenciada de adjudicación/contrato comprobado; no sobreescribir registros adjudicados con resultados no verificados.
4. `OrdenesCompra` (nueva tabla separada, aprobada ahora por el usuario): definir encabezados definitivos después de verificar el mapeo del objeto oficial de órdenes de compra. Candidatos estrictamente sujetos a fuente: código OC, fecha, organismo comprador, proveedor, monto, moneda, estado, tipo/mecanismo, código proceso referenciado y URL de detalle oficial.
5. Enlaces `OrdenesCompra → Procesos`: solo mediante identificador de referencia oficial y existente; orden sin vínculo se conserva como transacción huérfana verificada y no se atribuye por similitud de nombre.
6. JSON público: exportar solo campos disponibles y requeridos por interfaz; no publicar RUT, secretos ni identificadores técnicos privados. Mostrar oportunidades y transacciones por separado para evitar doble contabilización.

## Secuencia de implementación sin operaciones destructivas
1. Conservar copia/respaldos de Sheets y medir conteos por modalidad, duplicados y enlaces actuales.
2. Ejecutar/validar la extracción existente de Compra Ágil para ventanas diarias o históricos autorizados; no inferir éxito de scripts solo por existir.
3. Implementar normalizador/ETL de órdenes de compra con claves idempotentes, extracción diaria e histórica desacopladas. Un error de fuente no debe borrar filas existentes.
4. Añadir tabla `OrdenesCompra` solo una vez cerrado el contrato real de la API.
5. Actualizar publicador y frontend: filtro de modalidad para Procesos y apartado de ÓrdenesCompra separado, con vínculo público cuando exista.
6. Orquestar extracción de Procesos, Ofertas, Resultados y ÓrdenesCompra una vez por día, tres intentos máximos por componente, registrar fracaso y reintentar la fecha fallida al día siguiente.
7. Confirmar cobertura, consistencia referencial, trazabilidad y no duplicación; habilitar cron solo entonces.

## Restricciones
- No ejecutar flujos de prueba para averiguar si la API entrega PDF.
- No activar cron ni cargas masivas sin verificación de contrato y cabeceras.
- No limpiar/eliminar columnas sin confrontarlas con frontend, publicador y ETL.
- Distinguir "oferta seleccionada", "adjudicación informada" y "OC emitida".
- No declarar Compra Ágil u OC cargadas solo porque hay scripts.
