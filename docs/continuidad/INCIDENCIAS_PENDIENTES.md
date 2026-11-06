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
