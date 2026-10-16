# Esquema de datos objetivo — Observatorio Mercado Público

**Estado:** propuesta de migración, sin alterar la base actual. Aplicar tras cierre de ETL y antes de importar los CSV históricos. No activar carga diaria antes de validar el nuevo esquema.

## Principios
- Clave de proceso: `codigo` (única en Procesos).
- Clave de oferta: `codigo` + `id_cotizacion` (evitar depender de que un ID sea globalmente único).
- Selección de oferta != adjudicación contractual verificada.
- Campos monetarios: importe CLP numérico sin símbolo ni separadores en Sheets/CSV; `$` solo en frontend.
- Fechas: ISO `AAAA-MM-DD`; timestamps `AAAA-MM-DDTHH:MM:SSZ` cuando exista hora.
- No fabricar datos ausentes; fuente, cobertura y verificación deben quedar explícitas.
- Mantener identificadores personales y RUT fuera del JSON público.

## Procesos (20 columnas vigentes; conservar posición A:T)
`codigo,nombre,estado,convocatoria,fecha_publicacion,fecha_cierre,fecha_ultimo_cambio,monto_disponible_clp,organismo_comprador,rut_organismo,unidad_compra,region,total_ofertas_recibidas,motivo_seleccion,url_detalle,fecha_sincronizacion,categoria,subcategoria,codigo_categoria_oficial,modalidad`

**Corrección semántica:** la API V1 no permite suponer que `FechaAdjudicacion` corresponda a `fecha_ultimo_cambio`; no volver a almacenar ese dato bajo un nombre incorrecto. `monto_disponible_clp` significa presupuesto, no adjudicación.

**Agregar tras T**: `fuente_registro`, `estado_cobertura_detalle`, `fecha_actualizacion_fuente` (solo si la fuente proporciona realmente este último dato).

## Ofertas (17 columnas vigentes; conservar A:Q)
`codigo,convocatoria,rut_proveedor,proveedor,monto_ofertado_clp,moneda,fecha_oferta,estado_oferta,fuente,fecha_extraccion,id_cotizacion,valor_neto_clp,impuestos_clp,despacho_clp,seleccionado,id_oc_interno,estado_api`

**Agregar tras Q**: `url_documento_oferta` (solo URL pública confirmada), `nivel_visibilidad` (pública/no disponible/restringida), `fecha_actualizacion_fuente` (si existe).

**Clave recomendada para upsert**: combinación `codigo` + `id_cotizacion`, no solo `id_cotizacion`.

## Resultados (14 columnas vigentes; conservar A:N)
`codigo,convocatoria,rut_adjudicatario,adjudicatario,monto_adjudicado_clp,fecha_resultado,motivo_seleccion,fuente,validado,id_cotizacion_ganadora,monto_oferta_seleccionada_clp,id_oc_interno,estado_verificacion_oc,fecha_extraccion`

**Agregar tras N**: `tipo_resultado` (sin_seleccion/oferta_seleccionada/adjudicacion_informada/contrato_verificado/desierto/revocado), `fuente_adjudicacion`, `codigo_oc_publica`, `url_documento_publico`, `id_linea_adjudicacion`, `clave_resultado`.

**Nueva clave de Resultados:** `codigo + clave_resultado`. Para Compra Ágil, la selección usa `seleccion:<id_cotizacion>`; para adjudicaciones de licitaciones, usar `adjudicacion:<identificador_línea>:<identificador_proveedor>` solo cuando ambos identificadores estén disponibles. No deduplicar por código de proceso solamente. No inferir una línea ni un adjudicatario cuando la API no los proporciona. En la importación histórica, los resultados sin clave deben revisarse o migrarse a una clave verificable antes de activar la carga diaria.

Las columnas C:F permanecen vacías si solo se verificó una oferta seleccionada. Una licitación oficialmente adjudicada no implica, por sí sola, que se haya identificado el contrato u orden de compra.

## Control
Conservar `A:B` durante la migración para los metadatos heredados; conservar `D:K` para auditoría histórica. **No usar Control como cola con escrituras mezcladas**.

Registro futuro por jornada en una pestaña adicional `Ejecuciones`:
`fecha_publicacion,modalidad,componente,estado,intentos,ultimo_http,fecha_ultimo_intento,registros_procesados,fecha_completado,observacion`.
Clave: `fecha_publicacion + modalidad + componente`. Estados: pendiente, en_curso, completo, fallido.
Esta hoja permite recuperar fechas fallidas sin releer años anteriores, y se mantiene privada.

## Importación CSV y activación
1. Finalizar ETL según este contrato y verificar compatibilidad de lectura del frontend/publicador.
2. Respaldar las 4 hojas actuales antes de limpiarlas.
3. Crear columnas nuevas al final y la hoja Ejecuciones; nunca insertar en medio durante transición.
4. Cargar CSV históricos con cabeceras estrictas y verificar duplicados, tipos y relaciones.
5. Validar conteos y coherencia por modalidad/fecha; publicar una instantánea.
6. Solo entonces reactivar `schedule` del incremental diario.

**Fuera de alcance de esta migración:** suponer acceso a archivos PDF privados o reconstruir ofertas no publicadas por ChileCompra.
