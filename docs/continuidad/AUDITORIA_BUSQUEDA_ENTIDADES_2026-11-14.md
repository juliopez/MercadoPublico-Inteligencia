# Auditoría de viabilidad — consultas conversacionales por nombres (14/11/2026)

## Objetivo
Evaluar, sin modificar producción, si el asistente puede responder consultas como «¿[nombre] participa en Mercado Público?» con evidencia trazable.

## Evidencia examinada
- `scripts/asistente_ia/backend/motor.mjs`: motor actual permite `resumen`, `modalidades`, `organismo`, `serie` y `ranking`; consume exclusivamente `data/catalogo-publico.json` y `data/analitica/{periodo}/{entidad}.json`. No busca registros individuales ni nombres libres de proveedores.
- `scripts/asistente_ia/backend/intencion.mjs`: contrato Gemini restringido a las cinco operaciones anteriores.
- `frontend-v2/data/catalogo-publico.json`: catálogo de períodos y rutas a partes de registros por entidad; se observó estructura `data/partes/{entidad}/{periodo}/NNNN.json`.
- Muestras de `frontend-v2/data/partes/{ofertas,resultados,procesos,ordenescompra}/2026-10/0001.json`, que confirman campos siguientes:

| Entidad | Campos para búsqueda | Campos de contexto y verificación |
| --- | --- | --- |
| Ofertas | `proveedor` | `codigo`, `id_cotizacion`, `seleccionado`, `monto_ofertado_clp` |
| Resultados | `adjudicatario`, `proveedor_seleccionado` | `codigo`, `validado`, `estado_verificacion_oc`, `monto_adjudicado_clp` |
| Órdenes de compra | `proveedor` | `codigo_oc`, `codigo_proceso`, `estado`, `fecha_creacion` |
| Procesos | `nombre`, `organismo_comprador` | `codigo`, `modalidad`, `estado`, `url_detalle` |

## Hallazgos
1. **Viable con ampliación de lectura**: las partes contienen nombres y referencias para construir respuestas verificables; el motor actual solo usa agregados y no expone búsquedas por nombre.
2. **No hay índice de nombres verificado** en esta revisión. No debe suponerse que exista un índice eficiente de personas o proveedores. Recorrer todas las partes desde el Worker para cada pregunta podría ser costoso y lento; medir tamaño, volumen y tiempos antes de elegir diseño.
3. **La identidad no está confirmada por coincidencia textual**: una persona puede aparecer como proveedor, nombre comercial o dentro de una razón social; homónimos, variantes ortográficas y tildes deben tratarse como coincidencias, no identidad acreditada.
4. **Semántica de resultados**: `adjudicatario` o `seleccionado` no bastan por sí solos para declarar adjudicación contractual verificada; respetar `validado` y `estado_verificacion_oc`.
5. **Ausencia de coincidencias no equivale a ausencia en Mercado Público**: delimitar siempre los períodos y entidades efectivamente consultados.
6. **No se ha ejecutado una búsqueda exhaustiva del nombre de ejemplo** ni verificado la presencia de una persona concreta.

## Propuesta técnica para fase siguiente (no implementada)
- Inventariar cardinalidad, tamaño y cobertura de partes por período y entidad.
- Crear un índice de búsqueda derivado, de solo lectura y con procedencia por registro (entidad, período, parte, código), con normalización de tildes, mayúsculas y espacios; preservar nombre original.
- Definir operación controlada `buscar_participante` para Gemini y motor, con validación estricta, límites de resultados y de períodos, y manejo de ambigüedad.
- Responder con registros coincidentes, categoría de participación (oferta, resultado u OC), estado de verificación y enlaces de fuente; no inferir identidades ni adjudicaciones.
- Añadir pruebas de coincidencia exacta, parcial, homónimos, ausencia de resultados, límites de lectura y trazabilidad antes de desplegar.
- Mantener separados ETL, cron, MER y datos productivos; cualquier generación de índice deberá diseñarse y aprobarse por separado.

## Estado
**Auditoría inicial de estructura completada; implementación pendiente de autorización específica y validación técnica.** Este documento no modifica ningún proceso operativo.
