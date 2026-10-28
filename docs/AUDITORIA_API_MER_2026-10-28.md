# Etapa 2 — Auditoría de compatibilidad API ↔ MER — 28/10/2026

## Estado y alcance
**Revisión real de las seis cabeceras del Google Sheets operativo 2026-10 mediante acceso de solo lectura**, confrontada con scripts v1/v2 del repositorio. Sin llamadas API productivas, sin escritura en Sheets, sin activación de cron. La Etapa 1, cerrada 27/10, permanece intacta.

## Cabeceras MER observadas (orden exacto)
- **Procesos (16)**: `codigo,nombre,estado,convocatoria,fecha_publicacion,fecha_cierre,monto_disponible_clp,organismo_comprador,region,total_ofertas_recibidas,motivo_seleccion,url_detalle,fecha_sincronizacion,categoria,subcategoria,modalidad`.
- **Ofertas (9)**: `id_cotizacion,codigo,id_proveedor,proveedor,monto_ofertado_clp,fecha_oferta,fuente,seleccionado,rut_proveedor_cot`.
- **Resultados (10)**: `codigo,id_cotizacion_ganadora,adjudicatario,monto_adjudicado_clp,fecha_resultado,motivo_seleccion,fuente,validado,monto_oferta_seleccionada_clp,estado_verificacion_oc`.
- **OrdenesCompra (13)**: `codigo_oc,codigo_proceso,id_proveedor,fecha_creacion,fecha_aceptacion,estado,proveedor,monto_total_oc_clp,tipo_oc,cantidad_lineas,total_lineas_neto,rut_sucursal_oc,codigo_proveedor_oc`.
- **Proveedores (6)**: `id_proveedor,rut_canonico,razon_social_canonica,nombre_fantasia,fuente_principal,estado_identidad`.
- **VinculosCOT_OC (7)**: `id_vinculo,codigo_cot,codigo_oc,origen_vinculo,estado_oc_historico,fecha_aceptacion_oc,relacion_confiable`.

**Nota:** el operativo real consta de seis tabs visibles; los scripts antiguos que exigen `Control` o `ControlV2` no se pueden ejecutar contra este libro sin rediseñar checkpoints fuera de esas seis tablas o recuperar una fuente de estado ya instalada. Los conteos `rowCount` de metadata son tamaños de grilla, no registros cargados.

## Incompatibilidades bloqueantes verificadas en código
1. `scripts/v2_detalle_sheets.py`: `O` usa 7 campos en orden `codigo,proveedor,monto_ofertado_clp,fecha_oferta,fuente,id_cotizacion,seleccionado`, frente a 9 campos reales comenzando por `id_cotizacion`. `R` usa 10 campos pero orden diferente al MER. **Bloqueo antes de llamar API/escribir**, evita corrupción de columnas.
2. El mismo script exige `book.worksheet("ControlV2")`; esa pestaña no existe entre las seis hojas visibles. No permitir que un checkpoint experimental cree tablas nuevas sin diseño autorizado.
3. `scripts/sync_resultados_licitaciones.py` exige una cabecera `Resultados` de 10 columnas con orden distinto, y también requiere `Control` inexistente. Su modelo de unicidad por `codigo` es insuficiente para resultados múltiples por proceso cuando exista identificador oficial por línea.
4. `scripts/sync_chilecompra_sheets.py`: **sí proyecta Procesos por nombre de columna**, útil para reaprovechar; sin embargo, requiere `Control` para paginación Compra Ágil, que el MER no tiene. La variable `SYNC_FECHA_2026` por defecto es `2026-10-15`; no usarla en producción sin fecha explícita y control de período. El `upsert_rows` preserva vacíos pero prepara actualización de todas las filas encontradas, incluso sin cambios.
5. `scripts/api_retry.py`: reintentos acotados (máximo 3) para HTTP 502/503/504 y errores de red, detención explícita ante HTTP 429. Reutilizar, no duplicar.
6. La API v1 de detalle no demuestra acceso universal a ofertas individuales de licitaciones; registrar indisponibilidad en lugar de inventarlas.

## Mapeo propuesto, sujeto a prueba de payload real
| Fuente y campo candidato | Tabla y columna existente | PK y validación |
|---|---|---|
| v2 listado `codigo`, nombre, estado y fechas | `Procesos` por nombre de columna | `codigo`, sin cambios destructivos |
| v2 detalle `proveedores_cotizando[].id_cotizacion` | `Ofertas.id_cotizacion` | `(codigo,id_cotizacion)`; ID no vacío, único |
| v2 detalle `razon_social`, `monto_total`, `fecha_creacion` | `Ofertas.proveedor,monto_ofertado_clp,fecha_oferta` | Moneda CLP debe estar acreditada antes de fijar monto |
| v2 detalle `rut_proveedor` | `Ofertas.rut_proveedor_cot`, vínculo a `id_proveedor` canónico | Normalización verificable, no inventar identidad |
| v2 detalle `proveedor_seleccionado` | `Ofertas.seleccionado` y `Resultados.id_cotizacion_ganadora` | Selección informativa ≠ adjudicación jurídica |
| v2 detalle `monto_total` oferta seleccionada | `Resultados.monto_oferta_seleccionada_clp` | No copiar a `monto_adjudicado_clp` |
| v1 adjudicación oficial con proveedor y monto explícitos | `Resultados.adjudicatario,monto_adjudicado_clp,fecha_resultado` | Distinguir adjudicación informada de OC/contrato verificado |

## Diseño seguro del próximo paso
1. Hacer **sondeo API de solo lectura**, con respuesta resumida/sin RUT ni datos privados, para una pequeña muestra de códigos conocidos y respuestas HTTP; determinar estabilidad del payload y moneda.
2. Preparar funciones puras de normalización por **nombre de cabecera real**, con pruebas offline para ambas fuentes; ninguna función debe emitir listas posicionales de esquema piloto.
3. Usar registro de checkpoints recuperable **externo a las seis tablas** o reutilizar uno ya operacional y verificado; documentar formato, bloqueos y reanudación. Sin esa pieza, no arrancar una extracción masiva.
4. Aplicar cuotas/reintentos y clasificación de estados: `verificado_con_datos`, `sin_registros_confirmados`, `sin_cobertura`, `pendiente`, `error_transitorio`. No transformar HTTP 504 en cero ofertas.
5. Una vez probados idempotencia, precedencia de datos y respaldo, evaluar un piloto supervisado de escritura en octubre, sin tocar históricos ni cron.

## Próxima entrega técnica
**Adaptador compatible con cabeceras MER vigentes y prueba de API en seco**, seguido de informe de cobertura. Solo después de verificar esa etapa se autorizará escritura incremental real.
