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

## Ampliación de auditoría remota — 23/11/2026

**Contador de cuatro problemas (no confundir hallazgo con solución):** P1 publicación 16:00 = abierto; P2 licitaciones 16:15 = verificación de tres jornadas completada, cierre integral de seis jornadas pendiente; P3 Compra Ágil 22:05 = abierto, evidencia de ejecuciones omitidas; P4 inventario global y consolidado = abierto. **0/4 cerrados integralmente**.

### P1: publicación 16:00 — causa exacta aún no acreditada

Se examinó `scripts/ubuntu_cron_integrado.sh` y `scripts/ubuntu_publicar_v2_post_etl.sh`. El primero convierte cualquier error del publicador en `PUBLICACION_V2_FALLIDA`/código 20. El segundo tiene bloqueos posibles: estado de sincronización, lock, árbol Git con cambios rastreados, `git pull --ff-only`, exportación MER/vínculos (con reintentos solo para 429), `git add/commit/push`. **El mensaje del orquestador no permite discriminar la causa**; requiere leer las líneas anteriores del log completo de 16, 19 y 20/11. No atribuir sin pruebas el fallo a GitHub, cuotas o concurrencia. La conciliación 09:00 del 23/11 sí publicó, pero eso no acredita que todos los derivados de las jornadas fallidas se hayan recuperado.

### P2: licitaciones 16:15 — logs GitHub revisados

Se consultaron jobs y logs de runs `44800371336` (20/11), `44596356785` (19/11) y `44378497389` (18/11). Los tres jobs tuvieron todos sus pasos `success`; el último lote reportó `PENDIENTES_API=0`, `PUBLICACION_REPOSITORIO_OK` y `LICITACIONES_API_PUBLICADAS`. Detalles guardados al final: 1.381 (20/11), 1.353 (19/11), 1.253 (18/11), con cero pendientes y cero errores en los informes finales. El proceso distingue registros del mes de otros períodos. Las jornadas 13, 16 y 17/11 figuran `success` en listado, pero aún no se inspeccionaron sus logs finales. No equivale a comprobación independiente de Pages para cada jornada.

### P3: Compra Ágil nocturna — success sin procesamiento

Runs `45158022768` y `45142604562`, ambos `schedule` del 23/11 UTC, finalizaron `success`, pero **todos los pasos posteriores al validador de ventana quedaron `skipped`**. En `45158022768` el log muestra `VENTANA_API_CHILE 2026-11-23T07:39:35-03:00 OBJETIVO 2026-11-22 ESTADO FUERA_VENTANA`. No hubo recuperación ni exportación en esos dos runs. Por contraste, run `44848066536` (disparo manual nocturno 20/11 Chile) ejecutó lotes, exportación y Pages; log: `PAGES_VERIFICADO 2026-11` con 22.717 procesos, 117.618 OC, 46 ofertas y 0 resultados en aquella instantánea. El YAML `api-compra-agil-400-actions.yml` tiene cron UTC 01:05 y 02:05 y permite `workflow_dispatch` desde Ubuntu 22:05. **No concluir que dos cron UTC equivalen a dos cargas ni desactivar nada sin auditoría de ventanas/checkpoints.**

### P4: alcance

Se verificaron directamente YAML de `licitaciones-api-1615-actions.yml`, `api-compra-agil-400-actions.yml` y scripts locales. El censo exhaustivo de `.github/workflows` continúa pendiente por limitación de enumeración de directorios de la conexión GitHub; los 28 nombres del inventario documental no son un censo completo.

### P2 — cierre de verificación de seis jornadas (ampliación)

También se inspeccionaron logs finales de `44156552736` (17/11), `43937353697` (16/11) y `43490405837` (13/11). Los tres muestran `LICITACIONES_API_PUBLICADAS`, `PENDIENTES_API=0`, `PUBLICACION_REPOSITORIO_OK` y `errores=0` en el último informe. Detalles guardados: 1.274 (17/11), 1.891 (16/11), 1.330 (13/11). **Se cierra la comprobación de procesamiento y publicación en repositorio de las seis jornadas 13,16–20/11**; la comprobación específica de Pages por jornada es otra prueba y no se afirma realizada. **Contador actualizado: 1/4 problemas cerrados dentro del alcance definido; 3/4 abiertos** (P1, P3, P4).

## Revisión de ventana nocturna y diagnóstico pendiente (continuación)

Se leyó `scripts/ventana_api_nocturna.py`: autoriza solo hora local chilena **22:00–04:59** y objetivo de jornada hábil. El run programado `45158022768` inició a las **07:39 Chile** y su log registra `FUERA_VENTANA`; sus pasos de carga `skipped` son **conducta deliberada de protección**, no fallo de ejecución. El segundo run programado `45142604562` también tiene pasos de carga omitidos; no se atribuye causa concreta sin su línea de validador. Las dos entradas UTC del YAML son una estrategia estacional; la ejecución efectiva debe evaluarse por jornada chilena y pasos realizados, no por número de runs `success`. El disparador Ubuntu consulta runs previos y evita duplicar una jornada, pero se debe confirmar la interacción exacta con schedules. **No desactivar horarios por esta evidencia**.

Se inspeccionó `scripts/ubuntu_publicar_v2_post_etl.sh`: verifica sincronización fresca, lock de publicación, árbol Git limpio, `git pull --ff-only`, exportaciones con reintentos 429, commit y push. La evidencia disponible de `PUBLICACION_V2_FALLIDA` es un mensaje genérico del orquestador; **sin las líneas previas del log local no se puede identificar la causa ni aplicar una corrección segura**. Para diagnóstico sin cambios: `grep -n -B 65 -A 6 'PUBLICACION_V2_FALLIDA' logs/orquestador_integrado_202611{16,19,20}_1600*.log` (en Ubuntu, dentro del repositorio). No ejecutar publicador ni ETL de nuevo hasta conocer el error.

## Causas raíz confirmadas con logs locales completos — 23/11/2026

Fuente: salida del comando `grep -n -B 65 -A 6 'PUBLICACION_V2_FALLIDA' logs/orquestador_integrado_202611{16,19,20}_1600*.log` aportada por el operador.

| Jornada | Evidencia exacta | Causa | ETL/conciliación |
|---|---|---|---|
| 16/11 | `BLOQUEADO: cambios locales rastreados, conservar para revisión` (línea 158) | Guardia Git del publicador: `git status --porcelain --untracked-files=no` no vacío; salida 6 del publicador y 20 del orquestador | `CONCILIACION_VERIFICADA`, 218 vínculos nuevos confirmados |
| 19/11 | `gspread.exceptions.APIError: APIError: [503]: The service is currently unavailable.` (línea 3217), al abrir hoja `VinculosCOT_OC` | Error transitorio de Google Sheets en `exportar_vinculos_documentales_v2.py`; reintentos actuales del publicador solo reconocen 429/cuotas | `EXPORTACION_V2_VERIFICADA` para MER; falló la exportación posterior de vínculos |
| 20/11 | `BLOQUEADO: cambios locales rastreados, conservar para revisión` (línea 165) | Mismo bloqueo preventivo de Git del 16/11 | `CONCILIACION_VERIFICADA`, 646 vínculos nuevos confirmados |

**Diagnóstico cerrado; reparación operativa aún pendiente.** No se atribuye causa a GitHub Pages ni a los ETL de extracción. Los bloqueos del 16/20 son un mecanismo de protección correcto frente a modificaciones rastreadas; eliminarlo, forzar `git reset --hard` o hacer `git stash` indiscriminado sería inseguro. Se necesita identificar exactamente los archivos locales modificados y su procedencia antes de establecer una sincronización no destructiva. El error 503 es recuperable mediante reintentos acotados con espera y distinción entre errores transitorios y permanentes, pero requiere cambio de código y prueba. La exportación de MER ya verificada no justifica repetir el ETL ni reescribir Sheets.

**Plan de remediación, sujeto a aprobación específica para modificar código productivo:** (1) diagnosticar `git status --short` y `git diff --name-only` de Ubuntu sin alterar archivos; (2) diseñar una publicación que aísle la generación/exportación del árbol Git sucio y no sobrescriba cambios ajenos; (3) ampliar reintentos solo para HTTP 429, 500, 502, 503 y 504, con tope de tiempo y registro de causa; (4) ejecutar pruebas en seco y validar publicación posterior, conteos y Pages. Mantener **contador de problemas resueltos 1/4**: P1 causa identificada, reparación pendiente; P2 cerrado; P3 y P4 abiertos.

## Propuesta de reparación aislada — PR #26

Se abrió **PR borrador #26**: `fix/publicador-v2-reintentos-503-auditoria-20261123`, commit `8f4c1efe`. Modifica exclusivamente `scripts/ubuntu_publicar_v2_post_etl.sh` para reconocer respuestas transitorias HTTP 500, 502, 503 y 504 además de 429, manteniendo cuatro intentos y espera creciente (70, 140 y 280 segundos). No cambia el guardarraíl `git status`, ni se fusionó o desplegó. **Pendiente prueba y revisión**. La remediación de bloqueos Git 16/20 depende de un inventario de cambios locales en Ubuntu y no admite `reset --hard` ni limpieza automática indiscriminada. Contador **1/4**.
