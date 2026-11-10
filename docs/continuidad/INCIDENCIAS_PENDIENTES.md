# Pendientes y riesgos operativos

**Corte:** 2026-11-06. Esta lista recoge **validaciones abiertas**, no afirma que exista un fallo activo.

| ID | Prioridad | Pendiente / riesgo | Criterio de cierre | Referencia |
|---|---|---|---|---|
| VAL-01 | Alta | Primera conciliación histórica integral desatendida | Evidencia de disparo, tres ZIP, seis tablas, respaldo, publicación e índices, Pages y constancia final | [P4](../INVENTARIO_PROCESO_4_CONSOLIDACION_HISTORICA.md) |
| VAL-02 | Alta | Próxima rotación mensual disparada por timer | Único operativo, histórico conservado, catálogo correcto y logs sin intervención | [P3](../INVENTARIO_PROCESO_3_CAMBIO_MES.md) |
| VAL-03 | Alta | Coexistencia de conciliación extensa con ETL 16:00 | Demostrar exclusión, reintentos y ausencia de ejecución perdida | [Política](../POLITICA_PROTECCION_CUATRO_PROCESOS.md) |
| VAL-04 | Media | Trazabilidad de publicación e índices tras cambios de período | Igualdad de catálogo, fragmentos, derivados y contenido servido por Pages | [Automatización](../AUTOMATIZACION.md) |
| VAL-05 | Media | Auditoría de última noche y última corrida Ubuntu | Run IDs, logs, checkpoints, conteos y resultado por proceso | [Auditoría](AUDITORIA_OPERATIVA.md) |
| DOC-01 | Media | Ensayo de clon e instalación desde entorno limpio | Evidencia reproducible y ajustes a instrucciones de instalación | [Instalación](../INSTALACION.md) |

## Regla de mantenimiento

Cuando se resuelva un pendiente, agregar fecha, fuente de prueba, resultado y commit; moverlo a un apartado de **cerrados con evidencia**, no eliminarlo sin trazabilidad. No inventar resultados, ni usar la falta de registros como evidencia de cero actividad.

## Cerrados con evidencia documentada

- **UX-01 — Barras de progreso:** el responsable confirmó el 06/11/2026 que las consultas en el frontend funcionaron correctamente después de la estandarización. No reabrir sin una regresión verificable.

## Hallazgos de contraste 2026-11-06 (sin modificación productiva)

- **VAL-06 — Media, metadatos de catálogo:** `config/catalogo_sheets.json` mantiene `filas: 0` y estado `preparado_vacio_para_2026-11`, mientras el catálogo de exportación versionado registra 32.345 OC para noviembre en commit `0477f68`. Verificar si son campos estáticos de inicialización o deben actualizarse; no corregir sin revisar contrato y dependencias.
- **VAL-07 — Media, discrepancia de instalación del disparador:** estado documentado en continuidad (reportado operativo) y política maestra (pendiente de instalación) no coincide. Resolver únicamente con evidencia local Ubuntu y run ID de Actions; actualizar ambas fuentes tras comprobación.
- **VAL-04 y VAL-05 permanecen abiertos:** commits `0477f68` y `bc65f4f` evidencian actualización de exportación e índices el 06/11 16:04 Chile, pero faltan logs de ejecución, validación HTTP Pages e integridad de fragmentos.

Referencia: [registro de auditoría 06/11](AUDITORIA_OPERATIVA.md). No se ha confirmado un fallo productivo.


## Riesgos incorporados el 10/11/2026

| ID | Prioridad | Riesgo | Criterio de cierre |
|---|---|---|---|
| PUB-429 | Alta | Cuota de lectura Sheets bloquea publicación tras ETL exitoso | `main` actualizado en Ubuntu; reintentos registrados y publicación completada sin intervención |
| PUB-PAGES | Alta | Despliegue Pages #371 agotó tiempo; #372 tuvo éxito | Inspección y protección del workflow, comprobación final de artefactos publicados |
| DOC-ESTADO | Media | Documentación puede anticipar instalación local no comprobada | Registrar evidencia Ubuntu y actualizar estado explícitamente |
| EXP-01 | Baja | Escritor protegido aún no probado en copia MER | Validación y decisión sobre PR #1 |
| EXP-09 | Media | Tordo aún sin cobertura/frescura acreditada | Comparación con fuente oficial y decisión sobre PR #9 |

Ver [iniciativas](INICIATIVAS_EN_DESARROLLO.md) y [incidente](INCIDENTE_PUBLICACION_V2_2026-11-10.md).
