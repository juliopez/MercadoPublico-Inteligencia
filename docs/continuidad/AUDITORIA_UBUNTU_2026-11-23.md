# Auditoría operativa Ubuntu — 23/11/2026

**Estado:** inventario de configuración confirmado con salidas locales; auditoría de resultados **parcial**. Fuentes: salidas de `crontab -l`, `systemctl --user cat/list-timers`, `journalctl`, logs y estados compartidos en sesión; contraste con scripts y YAML de `main`. Horario `America/Santiago`. No se modificaron configuraciones ni se ejecutaron ETL en esta auditoría.

## Inventario de seis automatizaciones locales

| ID | Programación | Origen | Comando / servicio | Función | Evidencia |
|---|---|---|---|---|---|
| U1 | Cron cada hora, filtro interno L–V 16:00 | crontab | `scripts/ubuntu_cron_integrado.sh --cron` | ETL de dos fuentes, conciliación y publicación | Logs 12–20/11 |
| U2 | L–V 09:00 | crontab | `scripts/ubuntu_conciliar_mer_0900_aislado.sh` | Conciliación cronológica, exportación y publicación | 23/11 09:00–09:12:26 |
| U3 | L–V 16:15 | crontab | `scripts/ubuntu_dispatch_licitaciones_1615.sh` | **Solo solicita** `workflow_dispatch` de `licitaciones-api-1615-actions.yml`; no procesa API localmente | Dispatch OK 13,16–20/11; seis runs GitHub `success` |
| U4 | Diario 10:15 y `OnBootSec=10min`, `Persistent=true` | systemd usuario | `mercadopublico-conciliacion.timer/service` → `scripts/ubuntu_preparar_conciliacion_persistente.sh` | Evalúa cierre histórico; solo ejecuta `cierre_mensual_automatico.py` si estado `PENDIENTE_CONCILIACION` | 23/11 08:43 `COMPLETADO`, `accion=NINGUNA`; 10:15 programado, no inferir ejecución aún |
| U5 | L–V 19:00, `Persistent=true` | systemd usuario | `mercadopublico-rotacion.timer/service` → `scripts/ubuntu_rotacion_mensual.sh` | Evaluación de rotación del mes operativo | 16–20/11 `NO_CORRESPONDE_ROTACION`; último hábil 30/11 |
| U6 | L–V 22:05 Chile, `Persistent=true` | systemd usuario | `mercadopublico-api-github-dispatch.timer/service` → `scripts/ubuntu_disparar_api_actions.py --ejecutar` | **Solo solicita** `workflow_dispatch` de `api-compra-agil-400-actions.yml` | 16–20/11 `WORKFLOW_DISPATCH_SOLICITADO`; GitHub debe verificarse aparte |

**Alcance:** seis tareas del Observatorio en crontab de usuario y timers systemd usuario mostrados. No es censo de cron de root, `/etc/cron.d`, otros usuarios ni servicios systemd de sistema. Timers ajenos (Ubuntu Insights, Snap, Launchpad) no pertenecen al Observatorio.

## Hallazgos y resultados

1. **16:00: incidencia de publicación recurrente.** Logs del orquestador: 16/11, 19/11 y 20/11 `PUBLICACION_V2_FALLIDA` y `ERROR_PREVIO_ORQUESTACION exit=20`; 17/11 y 18/11 `PUBLICACION_V2_OK_O_SIN_CAMBIOS`. Los estados de sincronización/conciliación son independientes del éxito de publicación. El 20/11 `estado_sincronizacion.json` informó `EXITOSA`, `COMPLETA_VERIFICADA`, licitaciones y OC disponibles; `Procesos.nuevos=12`, `OrdenesCompra.nuevos=38892`, y `estado_conciliacion.json` `CONCILIACION_VERIFICADA`. **No declarar éxito integral** en jornadas con publicación fallida. No se ha establecido causa raíz ni eventual recuperación posterior para esas jornadas.
2. **09:00:** cron inició 23/11 a 09:00:01; log terminó `CONCILIACION_PUBLICADA 2026-11-23T09:12:26-03:00`, commit `f087a7754`. La ejecución publicada redistribuyó registros entre meses. La conciliación cronológica no es el cierre histórico systemd.
3. **16:15:** `ubuntu_dispatch_licitaciones_1615.sh` solo ejecuta `gh workflow run licitaciones-api-1615-actions.yml`. Seis despachos del 13,16–20/11 constan `OK`; las seis ejecuciones consultadas en GitHub figuran `completed/success`. El YAML remoto sí contiene bucle de recuperación, carga MER, checkpoint, exportación y commits. **Sin auditoría de lotes, conteos o Pages de cada run**.
4. **10:15:** `OnBootSec=10min` explica arranque adicional 08:43 del 23/11; se comprobó `COMPLETADO` con `accion=NINGUNA`. Los días 17–20/11 constan comprobaciones sin cierre; 17/11 10:15 informó `MER ocupado` y finalizó sin acción. Los días 21–22/11 `NO_CORRESPONDE`. El archivo `salida_operativa/estado_cierre.json` no existe en ruta consultada. Falta observar un cierre mensual que sí corresponda.
5. **19:00:** evaluaciones 16–20/11 sin rotación porque `ultimo_habil=2026-11-30`. No hay prueba de rotación efectiva en período auditado.
6. **22:05:** cinco despachos 16–20/11 confirmados desde Ubuntu; no equivalen a cinco recuperaciones completas. El workflow remoto `api-compra-agil-400-actions.yml` tiene además schedules UTC 01:05 y 02:05 por horario estacional; existen múltiples ejecuciones `schedule` con `success`, algunas en horas de madrugada. **Riesgo de duplicidad de disparadores y ejecuciones omitidas:** auditar selector, checkpoints, pasos skipped y procesamiento real antes de cambiar programación. La salida `gh run list` muestra seis runs `schedule` recientes, pero `success` no acredita inserciones.

## Dependencias y controles

- `U1` tiene candado de orquestación `logs/.orquestacion_diaria.lock`, además de candados internos de escritura.
- `U4` y `U5` utilizan `logs/.mer_escritura_compartida.lock`, `flock -n`; cuando está ocupado, omiten/reprograman por próxima oportunidad. El código `U4` comprueba `PENDIENTE_CONCILIACION` antes del cierre.
- `U3` y `U6` dependen de `gh` autenticado y de GitHub Actions. Los logs locales prueban **solicitud**, no publicación.
- `U6` consulta ejecuciones remotas activas y jornadas ya disparadas para evitar duplicados; el workflow remoto también tiene concurrencia `mer-api-actions-unica`.
- El cron integrado aparece en el journal cada hora; el script descarta horas distintas de 16 y fines de semana. No se identificó solapamiento productivo con 09:00 por ese motivo.
- El equipo estaba encendido desde aproximadamente 08:32 del 23/11; los horarios solo se cumplen localmente cuando Ubuntu y sus servicios están disponibles. `Persistent=true` permite activaciones de recuperación en systemd, sujetas a lógica de negocio.

## Pendientes y prioridades

**P1:** diagnosticar causa de `PUBLICACION_V2_FALLIDA` de 16/19/20 noviembre y verificar si una publicación posterior recuperó todos los datos. **P2:** auditar logs de jobs y conteos/checkpoints de `licitaciones-api-1615-actions.yml` y `api-compra-agil-400-actions.yml`, especialmente runs `schedule` con `success` y las solicitudes Ubuntu 22:05. **P3:** observar cierre y rotación cuando correspondan; comprobar destino real de `estado_cierre.json`. **P4:** completar inventario global de workflows GitHub (la auditoría Actions de 23/11 también es parcial), luego inventario consolidado con responsabilidades, conflictos y redundancias.

**Política:** no alterar cron, systemd, workflows ni productivo sin autorización explícita. Documento refleja evidencia disponible al 23/11, no validación futura.
