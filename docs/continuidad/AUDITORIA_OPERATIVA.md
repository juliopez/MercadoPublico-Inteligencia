# Auditoría operativa — evidencias y procedimiento

**Registro inicial:** 2026-11-06. **Este documento no declara una nueva auditoría en vivo**; consolida evidencias documentadas y establece el método para la siguiente.

## Evidencia disponible al corte

| Componente | Evidencia documentada | Límite |
|---|---|---|
| Cron 16:00 | [Línea base protegida](../LINEA_BASE_PROTEGIDA_CRON_1600.md) | No se adjuntó en esta actualización el último log local |
| API lote 400 | [Línea base](../LINEA_BASE_VALIDADA_API_COMPRA_AGIL_400.md) y confirmación del disparador nocturno | Verificar run reciente y checkpoint antes de certificar una noche específica |
| Rotación | [Inventario P3](../INVENTARIO_PROCESO_3_CAMBIO_MES.md): octubre→noviembre corroborado | Próxima ejecución autónoma pendiente |
| Conciliación | [Inventario P4](../INVENTARIO_PROCESO_4_CONSOLIDACION_HISTORICA.md): instalación documentada | Primera ejecución integral pendiente |
| Índices | [Auditoría de participación 06/11](../AUDITORIA_PARTICIPACION_2026-11-06.md) | Revisar sincronía de la publicación específica |
| Frontend | Responsable confirmó consultas y barras funcionales el 06/11 | Prueba de interfaz no reemplaza auditoría de integridad |

## Protocolo para la próxima auditoría

1. Registrar **fecha y hora de Chile**, rama y SHA de `main`.
2. Obtener últimos runs de Actions: ID, workflow, inicio, conclusión, commit y logs relevantes.
3. Obtener evidencia local Ubuntu: estado de timers, última/ próxima activación, `journalctl`, cron, checkpoints, locks y errores.
4. Cruzar por período: fuentes descargadas → registros MER → exportación → catálogo/fragmentos → índices → Pages.
5. Revisar integridad: seis hojas MER, cuatro entidades públicas, conteos, claves, duplicados, cobertura y montos.
6. Para rotación: verificar **único** MER operativo, histórico conservado, Drive, catálogo, fecha de ejecución y disparador real.
7. Para conciliación: verificar ZIP/CRC/SHA, respaldos, diferencias, escritura, constancia terminal y consulta HTTP posterior.
8. Clasificar cada hallazgo como `verificado`, `parcial`, `pendiente de evidencia` o `fallido`.
9. Registrar incidencias con evidencia y **pedir autorización antes de corregir componentes protegidos**.

## Plantilla de registro de auditoría

```text
Fecha/hora Chile:
Auditor / fuente de evidencia:
Commit main:
Período:
Proceso y disparador:
Run ID / journal / log:
Inicio y fin:
Registros leídos, escritos, publicados:
Checkpoint y reintentos:
Catálogo e índices verificados:
Resultado: verificado | parcial | pendiente | fallido
Incidencia y prioridad:
Acción autorizada:
Commit de corrección:
Prueba de regresión y reversión:
```

No registrar como éxito un proceso solo porque el timer está `enabled` o Actions reporta `success`.
