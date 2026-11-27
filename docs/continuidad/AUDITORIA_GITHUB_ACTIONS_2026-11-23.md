# Auditoría e inventario preliminar de GitHub Actions — 23/11/2026

## 27/11/2026 — recurrencia de disponibilidad transitoria del artefacto Pages

Run 46082016750/job 140783378577: carga exitosa 20:24:51.836, artefacto 15237394082 (320999505 bytes), API Actions disponible 20:24:52.275, deploy-pages encontró cero artefactos 20:24:52.632. Consulta posterior confirma artefacto existente y no expirado. La mitigación a06fbfde por consulta REST sola fue insuficiente; hipótesis de propagación inconsistente entre APIs, no causa interna confirmada. Run previo 46081915368 del mismo SHA e7271d7e1 verificó despliegue y catálogo público; noviembre 29.622 procesos y 158.363 OC según catálogo Git. No repetir ETL ni carga MER.

Corrección autorizada 68d102bb exclusivamente en .github/workflows/preview-frontend-v2.yml: conserva verificación REST previa, espera adicional 30 s, hasta tres invocaciones deploy-pages sobre mismo artefacto (esperas 30/60 s tras fallos); dos primeras toleran error solo para permitir reintento; tercera falla explícitamente si no logra desplegar, guardia de éxito y comprobación pública sin caché intactas. URL de entorno admite salida de cualquiera de tres intentos; timeout job 20→30 min. Sin cambios en horarios, grupos de concurrencia, ETL, datos o Sheets. Push activa workflow. Pendiente validar ejecución corregida y recuperación real ante nuevo fallo transitorio; no se garantiza recuperación frente a fallos persistentes. Reversión: revertir 68d102bb previa autorización.


## 26/11/2026 — colisión de publicación vespertina

ETL 16:00 terminó ORQUESTADOR OK 16:27:16, exportación 36ff8cdab: noviembre 27.917 procesos, 150.166 OC, 467 ofertas, 43 resultados. Run 45883764460/job 140129262208 validó derivados pero push rechazado 16:28:20 (main esperado b358e9386, real 090c6dfb), tras publicaciones concurrentes de participación y analítica. Pages run 45883873342 exitoso, pero búsqueda/perfiles del repositorio quedaron con 27.913 procesos y 118.574 OC; diferencias 4 y 31.592. API 16:15 run 45882218904 en curso al auditar. Supervisor matinal corregido run 45820050042 success.

Corrección autorizada ce718522: exclusivamente .github/workflows/publicacion-v2-post-etl.yml. Hasta cinco intentos de push; cada intento obtiene main remoto, regenera y valida derivados, preserva períodos autorizados acumulados, sin rebase de derivados obsoletos ni force push. Esperas 10/20/30/40 s; agotamiento explícito; errores de validación mantienen bloqueo. Reset hard únicamente en checkout efímero del runner. Push de workflow dispara recuperación de índices sin repetir ETL ni escribir Sheets. Se conserva horario y grupo de concurrencia. Pendiente confirmar ejecución corregida y coherencia catálogo/búsqueda/perfiles/Pages; no se garantiza ausencia de colisiones futuras ni recuperación ante fallos persistentes. Reversión: revertir ce718522 previa autorización.


## 26/11/2026 — validación autónoma 09:00 y corrección del supervisor

Ubuntu: CONCILIACION_PUBLICADA 09:09:42, commit 64e939f8b. Publicador corregido ayer: run 45817071270 success, derivados e13ab616 09:12:32, períodos julio–noviembre; Pages run 45817690689 success. Catálogo noviembre 27.913 procesos. Se valida operación autónoma de la corrección b25ee1246. Supervisor separado run 45817542363/job 139901053600 falló 09:13:37 por guardia de período histórico, y su código también exigía exportación posterior a 16:00 fuera de contexto. Corrección autorizada c6567efb exclusivamente en verificar-publicacion-diaria-v2.yml: reconoce origen conciliación por metadatos Git (no autenticación criptográfica), revisa períodos afectados y operativo, analítica, fragmentos, búsqueda y perfiles de cuatro entidades; conserva bloqueo de históricos no reconocidos y control de frescura vespertino para schedule (y manual desde 18h). El control horario por sí solo no distingue una exportación API de una exportación ETL. No modifica cron, publicador, MER ni datos. Push propio activa verificación. Pendiente acreditar resultado del nuevo supervisor y control programado de tarde; no repetir conciliación. Reversión: revertir c6567efb previa autorización.


## Actualización vigente — 25/11/2026, recuperación de la conciliación 09:00

Incidente #91: publicador rechazó el último período exportado (octubre histórico). Corrección autorizada `b25ee1246` en publicacion-v2-post-etl.yml; reconoce conciliación y regenera derivados de períodos afectados, manteniendo guardas para otros orígenes. Commit de recuperación `2a3f7b4ae` a las 09:33:06 acredita publicación de derivados junio–noviembre. Captura del operador confirma frontend con 26.838 procesos de noviembre y fecha de publicación 25/11 09:12; coincide con catálogo, analítica y dimensión de Sheets menos encabezado. Incidente recuperado; siguiente conciliación natural debe acreditar funcionamiento sin intervención. No repetir conciliación ni reparación. La comparación de snapshots nocturno `bce75616b` y matinal `844dd7b7f` muestra noviembre 27.232 → 26.838 (-394), históricos +134 (junio +2, julio +2, agosto +5, septiembre +21, octubre +104), total -260. El conciliador conserva PK históricas existentes y retira del operativo solo tras verificar presencia en destino; los 260 son compatibles con deduplicación, no confirmados individualmente. No afirmar pérdida ni ausencia de pérdida sin cotejo por PK o evidencia local. Referencia: [runbook 09:00](CONCILIACION_CRONOLOGICA_0900.md). La mitigación de artefacto Pages del 24/11 (`a06fbfde`) es independiente; sin log de espera/reintentos no certificar su eficacia frente a nueva demora. P2/P4 de auditoría cerrados; P1 favorable con limitaciones locales y P3 nocturno/fin de semana en seguimiento. No confundir códigos de auditoría con IDs de inventario.


## Alcance y criterio de evidencia

Auditoría **parcial**, independiente del entorno Ubuntu. Se revisaron archivos de workflows y documentación del repositorio, además de los jobs y logs de ejecuciones identificadas. No fue posible enumerar exhaustivamente todos los YAML habilitados ni todas las ejecuciones recientes mediante la conexión disponible. **No interpretar este inventario como censo completo de Actions**. No se dispararon workflows ni se alteraron datos durante esta auditoría.

Distinguir: (1) workflow documentado; (2) YAML verificado en `main`; (3) ejecución verificada; (4) registros incorporados; (5) exportación y Pages verificados. `success` no acredita automáticamente (4) ni (5).

## Inventario documental de 28 workflows

Fuente: `docs/GITHUB_ACTIONS_MANTENIMIENTO.md` y dos workflows de recuperación revisados. Los siguientes 26 nombres son **referencias documentales**, no confirmación individual de existencia/habilitación actual:

- **Publicación/operación (7):** `front-pages.yml`, `publicar-frontend-v2.yml`, `preview-frontend-v2.yml`, `publicar-sheets-pages.yml`, `publicar-solo-sheets.yml`, `observatorio-unico.yml`, `etl-loba-puntual.yml`.
- **Datos/índices V2 (7):** `generar-analitica-v2.yml`, `publicar-relaciones-procesos-v2.yml`, `indexar-relaciones-v2.yml`, `publicar-perfiles-v2.yml`, `publicar-autocompletado-v2.yml`, `publicar-sugerencias-global-v2.yml`, `ampliar-busqueda-v2.yml`.
- **Validación/integración (4):** `validar-analitica-historicos-v2.yml`, `validar-ux-integral-v2.yml`, `validar-busqueda-v2.yml`, `validacion-mer.yml`.
- **Pruebas específicas (8):** `validar-ajustes-landing-v2.yml`, `validar-buscador-global-v2.yml`, `validar-combinaciones-busqueda-v2.yml`, `validar-comparador-v2.yml`, `validar-favoritos-csv-v2.yml`, `validar-paquete-analitico-v2.yml`, `validar-perfiles-v2.yml`, `validar-presentacion-detalle-v2.yml`.
- **Recuperación de fin de semana (2):** `compra-agil-recuperacion-sabado.yml`, `compra-agil-recuperacion-domingo.yml`.

**YAML examinados directamente:** `preview-frontend-v2.yml` (workflow_dispatch, workflow_run y push filtrado; Pages), `publicar-frontend-v2.yml` (exportación por entidad/mes, workflow_dispatch y push filtrado), ambos recuperadores de fin de semana (schedule UTC doble por horario de Chile, workflow_dispatch, concurrencia `mer-api-actions-unica`, timeout 540 min). La búsqueda de `publicar-sheets-pages.yml` por ruta exacta no devolvió archivo; no concluir eliminación definitiva ni inactividad sin censo.

## Ejecuciones verificadas e incidentes

| Ejecución | Identidad | Evidencia |
|---|---|---|
| `44977382632` | Workflow de sábado, ejecución tardía 21/11 23:43 Chile | Job `success` pero selector `SIN_AUTORIZACION_O_PENDIENTES`; recuperación y publicación omitidas |
| `44983026915` | Segundo disparo del workflow de sábado, 22/11 00:59 Chile | Mismo resultado: 0 recuperación; no corresponde a workflow dominical |
| `45105256358` | Workflow dominical; inicio 23/11 00:19 Chile | Selector eligió 01/11; 64 consultas, 64 procesos, 419 ofertas, 43 resultados, 0 errores finales, un 429 recuperado; checkpoint de 01/11 completo; exportación y Pages verificadas |

En la ejecución dominical, el salto a 02/11 produjo `KeyError: '2026-11-02'` al consultar una jornada sin checkpoint. Los pasos posteriores de exportación y Pages continuaron y verificaron 22.781 procesos, 117.618 OC, 465 ofertas, 43 resultados. Se corrigió el acceso al estado faltante en `main`: sábado `132babdafde83cf81f38f2b00867ff7e8adb52d6`, domingo `84da57fcd3ca69be2852cc7b40d7f79d6b58dd25`. **La corrección todavía requiere validación mediante nueva ejecución real**.

La conciliación cronológica local de las 09:00 del 23/11 redistribuyó registros y publicó cerca de las 09:12, según capturas de Ubuntu aportadas durante la sesión; esa evidencia pertenece a la futura auditoría Ubuntu. El catálogo posterior de `main` registró 22.354 procesos, 103.092 OC, 465 ofertas y 43 resultados. La diferencia de procesos (427) coincide con el traslado informado por la conciliación. La diferencia de OC (14.526) coincide con la suma de traslados de la conciliación: 12.741 a octubre, 1.172 a septiembre, 335 a agosto, 146 a junio y 132 a julio. No hay diferencia residual de 1.785 OC.

## Proceso de las 10:15: sin identificar

**No se verificó un workflow de GitHub Actions programado para las 10:15.** No inferir ejecución, éxito, ausencia ni ubicación a partir del servicio Ubuntu `mercadopublico-conciliacion.service` ejecutado a las 08:43: son evidencias distintas. El inventario documental contiene una referencia histórica a `mercadopublico-conciliacion.timer` (10:00) que puede estar desactualizada; contrastar con Actions y configuración real antes de resolver la discrepancia. No confundir 09:15 con 10:15.

## Pendientes para cierre de auditoría GitHub

1. Enumerar todos los archivos en `.github/workflows/` y todos los workflows registrados (activos, deshabilitados y manuales); cruzar nombres, IDs, disparadores, UTC/Chile, concurrencia, permisos y secretos.
2. Obtener últimas ejecuciones por workflow, conclusión de cada job, pasos omitidos, volumen de datos, errores y checkpoints.
3. Identificar o descartar con evidencia el workflow atribuido a las 10:15 y revisar sus últimas ejecuciones.
4. Reconciliar exportaciones, catálogo de `main` y Pages tras conciliación 09:00; la diferencia de 14.526 OC queda explicada por los traslados del log de conciliación: 12.741 a octubre, 1.172 a septiembre, 335 a agosto, 146 a junio y 132 a julio (total 14.526).
5. Validar el arreglo `KeyError` de fin de semana en la próxima ejecución real.
6. Solo después, contrastar con cron/systemd instalado en Ubuntu y elaborar inventario consolidado.

**Política:** auditoría de solo lectura; no eliminar, reprogramar ni ejecutar procesos productivos sin autorización.

## Verificación posterior a aprobación (23/11)

Se reabrieron los YAML vigentes `compra-agil-recuperacion-sabado.yml` y `compra-agil-recuperacion-domingo.yml`. Ambos ya contienen en el chequeo de enfriamiento posterior al cambio de jornada: `json.load(...).get('jornadas_actions',{}).get(os.environ['MER_API_FECHA_OBJETIVO'],{})` (línea 131). Esta es la corrección del `KeyError: '2026-11-02'` que se observó en el log del run `45105256358`; no es necesario duplicarla. La consulta inicial del estado de la jornada actual en la línea 106 se ejecuta **después** de `mer_api_recuperacion_fin_semana.py`, que debe crear su checkpoint. El siguiente ciclo llama al mismo script con la nueva fecha objetivo.

El run `45158022768` de la jornada ordinaria fue `success` a nivel job, pero `VENTANA_API_CHILE ... 07:39 ... FUERA_VENTANA`: procesamiento omitido. No interpretar `success` como éxito de ingestión. Pendiente validar en una próxima ejecución de fin de semana que `SIGUIENTE_JORNADA` se acompañe de un checkpoint creado y de procesamiento efectivo de la nueva fecha. No se dispararon workflows ni se alteró producción en esta revisión.

## Censo directo de archivos YAML en main (23/11)

Se enumeró directamente el endpoint GitHub Contents `.github/workflows/`: **74 archivos YAML**. Este censo reemplaza la lista documental parcial de 28 referencias; no acredita por sí solo que todos estén habilitados ni ejecutándose. Desglose por prefijo, solo clasificatorio:

### asistente (19)

`asistente-ia-adaptador-worker.yml`, `asistente-ia-auditoria-fragmentos-oc.yml`, `asistente-ia-auditoria-fuentes.yml`, `asistente-ia-backend-tests.yml`, `asistente-ia-comparar-pages.yml`, `asistente-ia-conexion-demo.yml`, `asistente-ia-consultas-reales.yml`, `asistente-ia-datos-reales.yml`, `asistente-ia-escenarios-analiticos.yml`, `asistente-ia-flujo-conversacional.yml`, `asistente-ia-flujo-local.yml`, `asistente-ia-intencion-gemini.yml`, `asistente-ia-lenguaje-natural.yml`, `asistente-ia-navegador.yml`, `asistente-ia-orquestador.yml`, `asistente-ia-post-chat.yml`, `asistente-ia-pruebas-motor.yml`, `asistente-ia-ui-aislada.yml`, `test-asistente-gemini.yml`.

### validaciones (27)

`validacion-mer.yml`, `validar-ajustes-landing-v2.yml`, `validar-analitica-historicos-v2.yml`, `validar-apertura-noviembre-2026.yml`, `validar-api-diaria.yml`, `validar-api-escalable.yml`, `validar-api-nocturna.yml`, `validar-api-preconciliacion.yml`, `validar-buscador-global-v2.yml`, `validar-busqueda-v2.yml`, `validar-cierre-historico-automatico.yml`, `validar-combinaciones-busqueda-v2.yml`, `validar-comparador-v2.yml`, `validar-conciliacion-diferida.yml`, `validar-cron-api-local.yml`, `validar-disparador-api-ubuntu.yml`, `validar-etl-fuentes-independientes.yml`, `validar-favoritos-csv-v2.yml`, `validar-paquete-analitico-v2.yml`, `validar-participantes-v2.yml`, `validar-perfiles-v2.yml`, `validar-presentacion-detalle-v2.yml`, `validar-rotacion-mensual.yml`, `validar-ux-integral-v2.yml`, `validar-ventana-api-nocturna.yml`, `verificar-acceso-gha-mer.yml`, `verificar-publicacion-diaria-v2.yml`.

### resto (28)

`ampliar-busqueda-v2.yml`, `api-compra-agil-400-actions.yml`, `api-mer-ejecucion-excepcional-20261028.yml`, `auditar-esquema-api-20261028.yml`, `auditoria-montos-operativos.yml`, `compra-agil-recuperacion-domingo.yml`, `compra-agil-recuperacion-sabado.yml`, `conciliar-multimes-ca-oc-v2.yml`, `etl-loba-puntual.yml`, `generar-analitica-v2.yml`, `indexar-relaciones-v2.yml`, `licitaciones-api-1615-actions.yml`, `observacion-api-2230.yml`, `preview-frontend-v2.yml`, `probar-campos-api-mer.yml`, `prueba-enriquecimiento-mer-20261028.yml`, `publicacion-v2-post-etl.yml`, `publicar-api-octubre-recuperacion.yml`, `publicar-autocompletado-v2.yml`, `publicar-frontend-v2.yml`, `publicar-oc-candidatas-v2.yml`, `publicar-participacion-v2.yml`, `publicar-perfiles-v2.yml`, `publicar-relaciones-procesos-v2.yml`, `publicar-sugerencias-global-v2.yml`, `reconstruir-seleccionados-20261029.yml`, `reparacion-mer-octubre-20261028.yml`, `reparar-analitica-organismos-v2.yml`.

**Disparadores verificados en YAML:** `licitaciones-api-1615-actions.yml` solo `workflow_dispatch` (cron externo Ubuntu); `observacion-api-2230.yml` solo `workflow_dispatch` (no confundir nombre con horario activo); `conciliar-multimes-ca-oc-v2.yml` manual y push de scripts; `publicacion-v2-post-etl.yml` workflow_run, push de datos, cron de comprobación `0,15,30,45 20,21 * * 1-5` y manual. `api-compra-agil-400-actions.yml` dos cron UTC 01:05/02:05 y manual, con filtro de ventana chilena. Recuperaciones sábado y domingo usan cron doble UTC y manual.

**Pendiente de censo completo:** consultar registro de workflows habilitados/deshabilitados, todos los disparadores de los 74 YAML, ejecuciones y contrastar cron/systemd local. No afirmar que 74 workflows estén activos. La causa del `KeyError` de recuperación ya tiene arreglo presente en los YAML de sábado/domingo, pero falta ejecución posterior que confirme tránsito entre jornadas.

## Clasificación de disparadores: 28 YAML operativos (23/11)

Se inspeccionaron directamente los **28 archivos** del grupo operativo/mantenimiento (clasificación por nombre, no habilitación). Cinco declaran `schedule`:

| YAML | Cron UTC |
|---|---|
| `api-compra-agil-400-actions.yml` | `5 1 * * *`, `5 2 * * *` |
| `compra-agil-recuperacion-sabado.yml` | `0 23 * * 6`, `0 0 * * 0` |
| `compra-agil-recuperacion-domingo.yml` | `0 23 * * 0`, `0 0 * * 1` |
| `publicacion-v2-post-etl.yml` | `0,15,30,45 20,21 * * 1-5` |
| `reparar-analitica-organismos-v2.yml` | `15 22,23 * * 1-5` |

Los otros 23 YAML del grupo no declaran `schedule`; usan `workflow_dispatch`, `push` o `workflow_run` según archivo. En particular `licitaciones-api-1615-actions.yml` y `observacion-api-2230.yml` solo tienen `workflow_dispatch`; `preview-frontend-v2.yml` tiene manual, `workflow_run` y `push`; `conciliar-multimes-ca-oc-v2.yml` manual y `push`.

**Advertencias:** el cron UTC no garantiza hora exacta de inicio; las dobles programaciones no significan dos recuperaciones útiles. La clasificación aún no cubre los 46 YAML de asistente/validaciones ni el registro de habilitación GitHub. Pendiente contrastar cron/systemd Ubuntu. No se ejecutó ni modificó automatización productiva.

## Cierre del censo de disparadores: 74 de 74 YAML inspeccionados

Se inspeccionaron los 46 YAML restantes (19 del grupo asistente y 27 del grupo validaciones/verificaciones). **Uno** de estos 46 declara `schedule`: `verificar-publicacion-diaria-v2.yml`, cron UTC `12 21,22 * * 1-5`. Los otros 45 no tienen `schedule` y usan disparadores manuales, `push` y/o `pull_request`.

**Total corregido: 6 YAML con `schedule` y 68 sin `schedule`**, entre los 74 archivos del repositorio. Los seis son: `api-compra-agil-400-actions.yml`, `compra-agil-recuperacion-sabado.yml`, `compra-agil-recuperacion-domingo.yml`, `publicacion-v2-post-etl.yml`, `reparar-analitica-organismos-v2.yml`, `verificar-publicacion-diaria-v2.yml`. La clasificación anterior de cinco era parcial y queda expresamente sustituida por este censo completo.

**Límites:** existencia de YAML no prueba habilitación efectiva, cumplimiento del cron ni éxito de procesamiento. Aún no se obtuvo el listado de estados `active/disabled` de GitHub Actions ni la configuración real de crontab/systemd Ubuntu; mantener el problema de inventario abierto hasta contrastar esos datos.

## Actividad real y bloqueo de publicación adicional (23/11)

La API de runs del repositorio devuelve 2.900 ejecuciones históricas; las últimas 100 pertenecen a 11 YAML distintos. Muestra de `publicacion-v2-post-etl.yml`: 10 runs recientes, 7 `success` y 3 `failure`. En el run `45172104059` (push 23/11 12:12 UTC), job `137683954020`, el paso de preflight falla con `BLOQUEO: período exportado ajeno al operativo o cierre excepcional`. Es un bloqueo de validación de período, **distinto** del error 503 del publicador Ubuntu y no debe arreglarse suprimiendo la guarda sin verificar el catálogo. Este hallazgo queda pendiente de auditoría específica; no acredita pérdida de datos. Los runs nocturnos pueden aparecer verdes aun cuando el selector `FUERA_VENTANA` omita toda la ingesta.

La API GitHub de `actions/workflows` para consultar estados `active/disabled` no fue accesible mediante la conexión actual; no inferir que los 74 YAML estén habilitados. La API de runs sí permitió contrastar actividad de 11 workflows. El inventario queda completo a nivel de archivos y disparadores, **parcial** a nivel de habilitación y sistema Ubuntu.

## Consolidación de evidencias y prevención de verificaciones repetidas — 23/11/2026

**Origen:** revisión de la conversación, archivo aportado `Texto pegado(4).txt` (8.057 líneas, historial de comandos y salidas) y auditoría Ubuntu aportada en `Texto pegado.txt`; contraste con `docs/continuidad/README.md`, esta auditoría y `AUDITORIA_UBUNTU_2026-11-23.md`. La evidencia local proviene de salidas del operador; no se ejecutaron comandos nuevos en Ubuntu.

### Comprobaciones ya efectuadas; no volver a solicitarlas

- **GitHub:** censo de **74 YAML** y revisión de disparadores de **74/74**: seis con `schedule`, 68 sin él. El estado de habilitación en el registro de Actions no está acreditado; esta distinción no invalida el censo de archivos. La actividad histórica ya fue consultada (2.900 runs; últimas 100 ejecuciones de 11 workflows).
- **Ubuntu:** `crontab -l`, `systemctl --user list-timers --all`, lista de servicios, archivos `.timer/.service`, `journalctl` y procesos fueron ejecutados y sus salidas aportadas. Se confirmaron **tres entradas cron** (orquestador horario con filtro 16:00; conciliación L–V 09:00; dispatch licitaciones L–V 16:15) y **tres timers systemd** (cierre 10:15 con recuperación al arrancar; rotación L–V 19:00; dispatch Compra Ágil L–V 22:05). La revisión de estos datos ya está en `AUDITORIA_UBUNTU_2026-11-23.md`.
- **Conciliación 09:00, 23/11:** el log local confirma `CONCILIACION_FINALIZADA`, `CONCILIACION_VERIFICADA`, exportación de seis períodos, `EXPORTACION_V2_VERIFICADA`, commit `f087a7754` y `CONCILIACION_PUBLICADA 2026-11-23T09:12:26-03:00`. Movimientos: 427 procesos y 14.526 OC, lo que explica la diferencia de conteos de noviembre antes/después de conciliar. No se requiere repetir esa comprobación.
- **Cierre 10:15:** el timer estaba programado para 10:15 y la activación por arranque a las 08:43 devolvió `COMPLETADO`/`accion=NINGUNA`; **no existe fundamento para buscar un workflow GitHub a las 10:15**: es una tarea systemd local. La activación programada de las 10:15 del 23/11 no está demostrada por el extracto de las 09:50.
- **Licitaciones 16:15:** seis jornadas (13 y 16–20/11) con logs finales y publicación en repositorio comprobados; se mantiene cerrado P2 en el alcance definido, sin exigir nuevamente los seis runs.
- **Publicador 16:00:** causas 16/20 (guardia Git) y 19 (Sheets HTTP 503) ya diagnosticadas. PR #26 fusionado y descargado en Ubuntu, y árbol rastreado limpio tras respaldo de archivos; **la ejecución autónoma posterior aún no está verificada**. No repetir diagnóstico ni limpieza.
- **Compra Ágil:** ejecuciones `schedule` verdes con carga omitida por `FUERA_VENTANA` y recuperación dominical que sí procesó 01/11, con transición fallida al 02/11. Corrección de acceso a checkpoint ya presente en los dos YAML; falta validar una recuperación posterior. No duplicar el parche.

### Estado para decidir próximos pasos

**P1 abierto** únicamente por falta de evidencia de ejecución productiva posterior a la reparación; **P2 cerrado**; **P3 abierto** por eficacia real de ventana nocturna y continuidad de recuperación; **P4 avanzado sustancialmente** (censo YAML, disparadores y seis automatizaciones Ubuntu realizados), pendiente solo la habilitación real de workflows y una matriz de redundancias/decisiones si aportan valor operativo. El contador histórico sigue **1/4**, sin convertir comprobaciones accesorias en nuevos problemas. No solicitar más comandos de inventario ni cambios de configuración hasta revisar toda la evidencia existente.

**Nota de control:** este apartado sustituye afirmaciones previas de que el censo de YAML, sus disparadores o el inventario cron/systemd siguen sin realizarse. No se alteraron workflows, ETL, cron, timers ni datos productivos.

## P4 — contraste funcional de seis workflows programados (23/11, continuación)

Se releyeron directamente los seis YAML con `schedule`. Clasificación por responsabilidad:

| Workflow | Responsabilidad | Concurrencia |
|---|---|---|
| `api-compra-agil-400-actions.yml` | Ingesta diaria nocturna Compra Ágil | `mer-api-actions-unica` |
| `compra-agil-recuperacion-sabado.yml` | Recuperación de jornadas pendientes, sábado | `mer-api-actions-unica` |
| `compra-agil-recuperacion-domingo.yml` | Recuperación de jornadas pendientes, domingo | `mer-api-actions-unica` |
| `publicacion-v2-post-etl.yml` | Derivados e índices tras ETL/cargas, con validación de origen | `publicacion-v2-post-etl` |
| `reparar-analitica-organismos-v2.yml` | Reparación selectiva de agregados incompletos | `mer-reparar-analitica-organismos` |
| `verificar-publicacion-diaria-v2.yml` | Supervisión de actualidad MER e índices | `supervision-diaria-v2` |

**Conclusión acotada:** no se acredita duplicación funcional que justifique desactivar alguno. Los tres procesos Compra Ágil comparten grupo de concurrencia y tienen selectores/ventanas distintos. Publicación, reparación y supervisión son funciones diferentes, aunque sus disparadores (`push`, `workflow_run`, `schedule`, `workflow_dispatch`) pueden coincidir temporalmente. Un `success` sin trabajo por ventana no equivale a duplicación de datos. No modificar horarios ni deshabilitar YAML por esta revisión.

**Estado pendiente preciso de P4:** únicamente el registro efectivo `active/disabled` de los workflows en GitHub Actions, que la conexión GitHub actual no permitió consultar. Los 74 archivos, sus disparadores, los seis programados y las seis automatizaciones locales ya fueron revisados; no repetir crontab/systemd ni solicitar inventarios ya entregados. La ausencia de estados de habilitación impide afirmar que los 74 estén activos; tampoco impide utilizar el inventario funcional como referencia.

## P4 — verificación final de estados mediante GitHub API (23/11/2026)

El operador ejecutó en Ubuntu una consulta **de solo lectura** a `gh api --paginate repos/juliopez/MercadoPublico-Inteligencia/actions/workflows?per_page=100 --jq '.workflows[] | [.name, .state, .path] | @tsv'` y aportó la salida completa en conversación. **Todos los registros devueltos indican `state=active`; ninguno figura `disabled`**. La comprobación previa de interfaz también mostró `Disable workflow` para `verificar-publicacion-diaria-v2.yml`, coherente con su estado activo.

**P4 cerrado dentro del alcance acordado:** inventario de archivos y disparadores, seis workflows con `schedule`, seis automatizaciones locales Ubuntu, clasificación funcional y revisión de posibles redundancias, y comprobación de estados efectivos por API. No se identificó redundancia funcional que justifique deshabilitar workflows. Que un workflow esté activo no significa que se ejecute periódicamente ni que su última ejecución haya procesado registros; esas comprobaciones pertenecen a P1/P3 y a su observación futura.

**Sin cambios productivos:** no se habilitó/deshabilitó workflow ni se alteraron cron, systemd o ETL. Se deja P1 (validación próxima ejecución 16:00) y P3 (validación de Compra Ágil/recuperación) pendientes de sus ejecuciones naturales.


## Actualización 24/11/2026 — incidente Pages y mitigación preventiva (P3 de auditoría)

**Evidencia:** [jornada Compra Ágil 45302393424](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/45302393424), job 138137865890: cuatro lotes de 400; pasos de lotes, resguardo y exportación exitosos; reporte del cuarto lote: 400 consultados, 400 procesos, 0 errores, `jornada_completa=false`. Commit de exportación `d9ee27b13` a las 03:15 Chile. El job nocturno concluyó failure exclusivamente en «Desplegar y verificar Pages». [Despliegue 45339115855](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/45339115855), job 138258212896: integridad y construcción correctas (45.700 archivos); carga de artefacto github-pages ID 14894808339 (318.647.942 bytes) finalizada 03:17:07; consulta de metadatos 03:17:08 devolvió cero artefactos. La API consultada posteriormente confirmó su existencia y vigencia. Evidencia compatible con disponibilidad eventual del artefacto; no se ha acreditado la causa interna de GitHub.

**Corrección autorizada e implementada:** commit [a06fbfde](https://github.com/juliopez/MercadoPublico-Inteligencia/commit/a06fbfdecb47de98ad9f57840b47c07c91092613), exclusivamente `.github/workflows/preview-frontend-v2.yml`. Permiso `actions: read` y comprobación previa a deploy-pages de exactamente un artefacto github-pages no expirado para el run actual, hasta 12 consultas separadas por 10 segundos, con marcas PAGES_ARTIFACT_DISPONIBLE/PAGES_ARTIFACT_REINTENTO y fallo explícito al agotar intentos. Se verificó el YAML en main. El push coincide con el filtro del propio workflow; no se solicitó una reejecución adicional ni se repitió la ingesta. No se modificaron ETL, Compra Ágil, cron, timers ni MER.

**Recuperación acreditada:** Google Sheets operativo pasó de 23.402 a 25.002 filas de datos (+1.600); se inspeccionaron registros Compra Ágil al final de la hoja. Captura del frontend aportada por el operador el 24/11 muestra 25.002 procesos únicos de noviembre, 7.021 licitaciones y fecha de publicación 03:15 Chile. Coincidencia del total; no equivale a auditoría individual de códigos. Las dos tarjetas superiores aparecían con guiones, sin afectar la evidencia del indicador inferior. No se obtuvo el log del nuevo despliegue que recuperó la visualización.

**Estado:** incidente de publicación recuperado; mitigación implementada, validación preventiva pendiente en próximas ejecuciones naturales. P3 de auditoría no cerrado integralmente: resta validar el nuevo paso en logs y la recuperación de fin de semana/transición de jornadas; no confundir con el P3 histórico de rotación mensual. P1: ejecución 16:00 del 23/11 favorable en GitHub y frontend posterior, sin log integral local; P2/P4 permanecen cerrados dentro de su alcance. No repetir cargas ni modificar producción sin autorización.
