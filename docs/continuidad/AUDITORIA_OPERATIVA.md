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

## Auditoría de contraste — 2026-11-06, 16:22 Chile (19:22 UTC)

**Alcance:** lectura de documentación protegida, catálogo versionado y commits recientes de GitHub. No se obtuvo acceso a la lista de ejecuciones de GitHub Actions ni a los journals del Ubuntu real. Por tanto, **no se certifican runs, timers ni ejecución local** en esta revisión.

- **Referencia Git observada:** commit `bc65f4fac6bffacbec3d71077511411f39d9052b` (2026-11-06 19:04:37 UTC), actualización de índices/agregados de noviembre. Precedido por `0477f68f14d0b01c076d880043e536e296ea0f95` (19:04:07 UTC), actualización de extractos MER.
- **Evidencia concreta de publicación versionada:** en el diff del catálogo público del commit `0477f68`, el número de registros `ordenescompra` del período `2026-11` pasó de **16.197 a 32.345**; se incorporaron fragmentos `0018.json` a `0033.json`. La marca `ultima_exportacion.fecha_utc` pasó a `2026-11-06T19:03:55.489596+00:00`.
- **Evidencia de índices:** el commit posterior `bc65f4f` modificó agregados de `ordenescompra` de noviembre de 16.197 a 32.345 registros. Se observa secuencia de commits de datos → índices, **sin comprobación HTTP de Pages ni prueba de integridad de todos los fragmentos**.
- **Catálogo operativo versionado:** `config/catalogo_sheets.json` identifica `2026-11` como operativo y `2026-10` como histórico pendiente de conciliación oficial. Sus campos `actualizado: 2026-10-30`, `estado: preparado_vacio_para_2026-11` y `filas: 0` no reflejan por sí solos los extractos publicados en noviembre. **Posible desactualización de metadatos**, no evidencia de que MER esté vacío.
- **Discrepancia documental:** `docs/continuidad/ESTADO_ACTUAL.md` indica disparador Ubuntu 22:05 reportado funcionando; la política maestra todavía dice «pendiente de instalación». Requiere cotejo con `systemctl --user`, `journalctl --user` y un run identificado, antes de resolver cuál es el estado real.
- **Cron 16:00:** la publicación de las 16:04 Chile es compatible temporalmente con el horario del cron, pero **no demuestra causalidad ni éxito del cron** sin log local.
- **API nocturna, rotación y conciliación:** sin nuevos run IDs, journals ni checkpoints verificables en esta sesión. Se mantienen sus validaciones abiertas.

**Clasificación:** publicación Git = **parcial verificada**; correspondencia Pages = **pendiente**; cron Ubuntu = **pendiente de evidencia**; API nocturna = **pendiente de evidencia**; rotación autónoma = **pendiente**; conciliación integral = **pendiente**.

**Acciones realizadas:** actualización exclusivamente documental. No se ejecutaron ni modificaron ETL, scripts, workflows, timers, locks, catálogo ni frontend.

**Referencias:** [commit MER](https://github.com/juliopez/MercadoPublico-Inteligencia/commit/0477f68f14d0b01c076d880043e536e296ea0f95) · [commit índices](https://github.com/juliopez/MercadoPublico-Inteligencia/commit/bc65f4fac6bffacbec3d71077511411f39d9052b).
