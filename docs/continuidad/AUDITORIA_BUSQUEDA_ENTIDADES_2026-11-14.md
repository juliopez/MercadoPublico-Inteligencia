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

## Avance de implementación aislada — 14/11/2026
- Prototipo `scripts/asistente_ia/backend/indice_nombres.mjs`: normalización, índice con procedencia y búsqueda exacta/parcial.
- `scripts/asistente_ia/backend/motor.mjs`: nueva operación `buscar_participante` disponible **solo cuando se inyecta** `leerIndiceNombres`; no hay índice real publicado ni conexión Gemini.
- `scripts/asistente_ia/backend/generar_indice_nombres.mjs`: generador local, explícito y no programado, basado en partes del catálogo; **no se ha ejecutado contra todas las partes reales**.
- Pruebas sintéticas del generador en `generar_indice_nombres.test.mjs`: comprueban tres entidades, procedencia, partes faltantes y rechazo de rutas externas. Las pruebas sintéticas no acreditan cobertura, rendimiento ni exactitud del índice real.
- Antes de usarlo en producción, comprobar tamaño del índice real, memoria, tiempos de generación, política de actualización y modo de lectura acotado desde Cloudflare; no incorporar generación a cron/ETL sin autorización.

## Auditoría de volumen con catálogo real (14/11/2026)
Catálogo examinado: `frontend-v2/data/catalogo-publico.json`, fecha de publicación `2026-11-14T08:46:24.555594+00:00`.

| Período | Ofertas | Resultados | Órdenes de compra | Partes de estas 3 entidades |
| --- | ---: | ---: | ---: | ---: |
| 2026-06 | 407.923 | 63.214 | 150.551 | 623 |
| 2026-07 | 437.855 | 54.526 | 151.050 | 645 |
| 2026-08 | 432.111 | 65.945 | 153.438 | 653 |
| 2026-09 | 398.018 | 48.637 | 148.772 | 597 |
| 2026-10 | 470.841 | 56.813 | 177.972 | 706 |
| 2026-11 | 28 | 0 | 75.472 | 78 |
| **Total** | **2.146.776** | **289.135** | **857.255** | **3.302** |

Total combinado: **3.293.166 registros**. Las partes del catálogo incluyen un archivo de resultados para noviembre aunque su conteo sea cero.

Se inspeccionaron directamente los primeros archivos de octubre de las tres entidades: 1.000 registros por archivo, 3.000 registros en total, con campos de nombres disponibles. Tamaños de las respuestas de GitHub: ofertas 221.880 caracteres, resultados 424.568 caracteres, OC 278.810 caracteres. Estas muestras **no prueban** que los 3.302 archivos sean legibles ni que el generador complete el procesamiento total.

**Riesgo de escalabilidad**: la versión inicial de `generar_indice_nombres.mjs` acumula todos los lotes y luego construye el índice; con 3,29 millones de registros puede agotar memoria. Antes de una ejecución completa, cambiar a procesamiento incremental, escribir índice particionado y establecer límites de memoria/tamaño. Evitar que el Worker descargue el índice íntegro en cada pregunta. Esta auditoría no ha generado ni publicado un índice real.

## Procedimiento de prueba completa aislada — pendiente de ejecución
**Prerrequisito:** disponer de una copia local íntegra de `frontend-v2/data/catalogo-publico.json` y de las partes de ofertas, resultados y órdenes de compra referenciadas para el período. No asumir que un checkout Git contiene todas las partes si fueron generadas fuera del repositorio.

Desde la raíz de una copia de trabajo que tenga los archivos de datos:

```bash
node scripts/asistente_ia/backend/generar_indice_nombres.mjs \
  "$PWD/frontend-v2" 2026-10 "$HOME/indice-nombres-prueba-2026-10"
```

El destino debe ser un directorio **nuevo**, fuera del frontend publicado. El comando no escribe en MER, Google Sheets, ETL, cron, Worker ni Pages. El manifiesto resultante debe registrar 470.841 ofertas, 56.813 resultados y 177.972 órdenes de compra: **705.626 registros de origen** para octubre, repartidos en **706 archivos de índice**. El total de entradas por nombre puede ser menor o mayor que el de registros (campos vacíos o dos nombres diferentes en un resultado).

**Criterios de aceptación:** finalización sin error; manifiesto con los 706 archivos y conteos exactos; comprobación de que cada archivo referenciado existe; muestreo de trazabilidad `parte`/`fila`/`codigo` contra la parte de origen; búsqueda exacta y parcial con límites; tiempo, RAM máxima y tamaño en disco registrados. Si faltan partes, abortar sin afirmar cobertura completa.

**Advertencia de arquitectura:** el índice actual se particiona por archivo de origen, **no por clave de nombre**. Esto acota la RAM del generador pero todavía no permite búsquedas eficientes en el Worker sin recorrer muchos archivos. Antes de la integración, construir un índice de acceso por clave o prefijo y comprobar sus costos. No activar consultas conversacionales por nombres hasta resolver ese punto.

## Integración técnica en PR #20 (14/11)
- Contrato Gemini `buscar_participante` limitado a búsqueda exacta por período; no identifica legalmente a personas ni certifica adjudicaciones.
- Generador incremental por partes y archivos `clave-xx.ndjson`; lector local y lector HTTP de Pages, ambos con pruebas aisladas.
- Motor y adaptador Worker admiten la función inyectada `buscarIndiceNombres`; el adaptador puede construirla desde `fetchIndice`.
- La publicación de índices en `frontend-v2/data/indices-nombres/<periodo>/` y la activación del Worker **no están realizadas**.
- El job `indice_octubre_aislado` se añadió al workflow de pruebas para validar 705.626 registros reales de octubre sin escribir en producción.
- Primer intento de índice real: fallo por un nombre de longitud menor a tres caracteres. Se corrigió la partición para aceptar nombres cortos en datos de origen, manteniendo las consultas del usuario con mínimo de tres caracteres. Revalidación pendiente.
- No fusionar ni desplegar sin comprobar cobertura real, tamaño de índices, tiempos y compatibilidad de la implementación Worker existente.
