# Memoria operativa consolidada — Observatorio Mercado Público

## Actualización vigente — 24/11/2026

[Incidente Pages, evidencia y corrección preventiva](AUDITORIA_GITHUB_ACTIONS_2026-11-23.md#actualización-24112026--incidente-pages-y-mitigación-preventiva-p3-de-auditoría): Compra Ágil nocturna del 23/11 publicó cuatro lotes (1.600 registros adicionales) en MER y GitHub, pero falló el despliegue por ausencia momentánea del artefacto recién cargado. Mitigación en `a06fbfde`: comprobar disponibilidad del artefacto antes del despliegue (12 intentos, intervalo 10 s). Frontend recuperado según captura del operador: 25.002 procesos en noviembre, fecha 24/11 03:15; coincide con el total de Sheets. **Incidente recuperado, prevención pendiente de validación autónoma; P3 de auditoría sigue en seguimiento**, incluida recuperación de fin de semana. P1 favorable con limitaciones de evidencia local; P2/P4 cerrados. Esta actualización prevalece sobre estados anteriores de auditoría, no cambia los identificadores de procesos históricos. Sin nuevas modificaciones productivas.

**Corte:** 23 de noviembre de 2026. **Ámbito:** proyecto `juliopez/MercadoPublico-Inteligencia`. **Propósito:** conservar contexto, decisiones, evidencias y pendientes para retomar sin repetir auditorías. Este documento es una síntesis; las fuentes primarias son código, logs, ejecuciones y auditorías enlazadas. Los hechos históricos no sustituyen el estado actual.

## 1. Contrato de trabajo
- Observatorio de uso **personal**; no proponer difusión ni publicación a terceros como objetivo. «Publicar» significa actualizar los artefactos del frontend GitHub Pages, no hacer promoción del proyecto.
- Prioridad: automatización desatendida, integridad y trazabilidad de datos, evitar reprocesamiento y regresiones.
- No modificar procesos productivos (ETL, cron, timers, workflows, MER, Google Sheets, frontend) sin autorización explícita. Una aprobación aplica al cambio acordado, no a cambios adyacentes.
- No confundir workflow `success` con procesamiento, inserción, exportación y visibilidad real. Distinguir `documentado`, `implementado`, `instalado`, `ejecutado`, `verificado` y `pendiente`.
- Preferir comprobaciones independientes y de solo lectura; no solicitar de nuevo información ya aportada ni repetir pasos cerrados.

## 2. Arquitectura y datos
- Repositorio `juliopez/MercadoPublico-Inteligencia`, rama `main`; frontend operativo `frontend-v2/` en GitHub Pages.
- Origen de datos: ChileCompra/Mercado Público (ZIP y API), carga en hojas Google Sheets/MER operativo e histórico, exportaciones JSON de catálogo, fragmentos y analítica en GitHub/Pages.
- JSON publicados sirven para el frontend y el asistente; no equivalen necesariamente a toda la granularidad ni a todos los registros de Google Sheets. No asumir identidad de instantáneas o ausencia de datos por diferencias de conteos.
- Asistente IA: Gemini mediante Cloudflare Worker y motor determinista; consulta actualmente fuentes JSON, no directamente Sheets. Objetivo pendiente: responder consultas abiertas en lenguaje natural sobre los datos, no limitarse a intenciones predefinidas. No prometer cobertura arbitraria sin motor de consulta/semántica y validación de fuentes.
- Referencias históricas de volumen verificadas en conversaciones: octubre 2026, 92.302 procesos (6.895 licitaciones, 85.407 compras ágiles); agosto 2026, 83.944; noviembre 2026, 9.078 en una instantánea del 13/11 (1.458 licitaciones y 7.620 compras ágiles). **Son cortes históricos**, no totales actuales.

## 3. Automatizaciones: disparadores y alcance
- **09:00 lunes–viernes Ubuntu:** conciliación cronológica del MER; redistribuye por fecha de registro y publica períodos afectados; no confundir con cierre mensual.
- **16:00 lunes–viernes Ubuntu:** `scripts/ubuntu_cron_integrado.sh --cron` ejecuta ETL ZIP de licitaciones/OC, conciliación y publicación V2. **Cambio confirmado el 23/11:** antes `0 * * * *` (invocación horaria con filtro interno), ahora `0 16 * * 1-5`. Línea exacta confirmada por el operador: `0 16 * * 1-5 /bin/bash "/home/julio/Julio Lopez/chilecompra/MercadoPublico-Inteligencia/scripts/ubuntu_cron_integrado.sh" --cron`. Se conserva filtro interno. Solo se cambió la frecuencia del cron, no el script.
- **16:15 lunes–viernes Ubuntu:** `ubuntu_dispatch_licitaciones_1615.sh` dispara `licitaciones-api-1615-actions.yml` en GitHub; ejecución remota procesa lotes, checkpoints, carga y publicación. No confundir despacho local con procesamiento remoto.
- **22:05 Chile:** existe workflow `api-compra-agil-400-actions.yml` con programación GitHub UTC estacional y posibilidad de disparo desde Ubuntu. Se documentaron previamente timer de usuario y despachos locales; una comprobación posterior de crontab/systemd filtrados no volvió a acreditar esos timers en ese equipo. **Verificar estado instalado si es necesario; no asumir que ausencia en crontab implica ausencia de schedule GitHub.**
- **Fin de semana 20:00 Chile:** workflows de recuperación Compra Ágil sábado y domingo; GitHub puede retrasar `schedule`. Corrección del selector con tolerancia a retrasos y checkpoint; validación posterior aún pendiente.
- **10:15 cierre mensual y 19:00 rotación:** hay documentación y ejecuciones históricas de timers de usuario, pero el estado instalado actual no quedó inequívocamente acreditado en el último contraste. No declarar operativos sin evidencia reciente.
- Inventario GitHub Actions: **74 YAML identificados en auditoría de repositorio** (6 con `schedule`, 68 sin él, según ese censo). Posteriormente, salida completa de `gh api --paginate .../actions/workflows?per_page=100` aportada por el operador mostró **todos los workflows registrados devueltos con `state=active`**, ninguno `disabled`. La lista API y el censo YAML pueden diferir; activo no significa programado ni ejecutado. Se revisaron los seis workflows con schedule sin redundancias funcionales confirmadas. P4 cerrado dentro de ese alcance.

## 4. Estado de los cuatro problemas de auditoría
| Código | Estado al corte | Evidencia y criterio |
| --- | --- | --- |
| **P1** ETL/publicación 16:00 | **Pendiente validación de ejecución automática** | 16 y 20/11: bloqueo Git por cambios rastreados; 19/11: Google Sheets HTTP 503 en exportación de vínculos. PR #26 incorporó reintentos 429/500/502/503/504; usuario actualizó Ubuntu, árbol rastreado limpio. El cambio de cron a 16:00 quedó confirmado. Falta comprobar una ejecución natural completa y publicación. |
| **P2** Licitaciones 16:15 | **Cerrado** | Se auditaron seis jornadas 13, 16–20/11: logs finales con `PENDIENTES_API=0`, `errores=0`, `PUBLICACION_REPOSITORIO_OK`, `LICITACIONES_API_PUBLICADAS`. No extrapolar a jornadas futuras. |
| **P3** Compra Ágil 22:05/recuperación | **Pendiente validación de ejecución automática efectiva** | Se observaron `success` con pasos `skipped` por ventana chilena; runs reales con lotes y publicación también existen. Correcciones del selector de fin de semana y checkpoints incorporadas; falta demostrar comportamiento posterior completo. |
| **P4** Inventario de automatizaciones | **Cerrado** | Inventario GitHub YAML, revisión de schedules y automatizaciones Ubuntu, salida API con estados activos, sin redundancia funcional confirmada. |

**Balance:** P2 y P4 cerrados; P1 y P3 en observación. No realizar cambios preventivos adicionales sin nuevos fallos.

## 5. Incidentes y decisiones técnicas relevantes
- 06/11 ZIP licitaciones vacío; 08–09/11 API Compra Ágil v2 presentó 504/NOT_FOUND; v1 es alternativa más lenta; se ensayó una vía «Tordo» aislada. No incorporar rutas experimentales sin pruebas y aprobación.
- 10/11 publicación bloqueada por 429 Sheets; se incorporaron reintentos. La conciliación 09:00 debe evitar bloquear la orquestación de 16:00.
- 12/11 falló publicación por Pages; 13/11 proceso nocturno terminó correctamente.
- 16–20/11 auditoría identificó fallos de publicación 16/19/20; no repetir extracción ETL para subsanar una exportación/publicación fallida sin analizar estado MER.
- 21–22/11 recuperación de fin de semana tuvo runs verdes pero sin procesamiento por ventana/selector. Correcciones de selector y acceso seguro a checkpoint se integraron; aún falta validar con una ejecución posterior.
- 23/11 conciliación 09:00 terminó `CONCILIACION_PUBLICADA` 09:12:26 -03:00, commit `f087a7754`. El catálogo remoto puede cambiar durante el día; comparar marcas de tiempo antes de interpretar diferencias de volumen.
- PR #26 para reintentos de 503 fue integrado y actualizado en Ubuntu según auditoría; conservar guardia Git de cambios locales, no usar `reset --hard`, `git clean`, `stash` indiscriminado ni `git add -A` sobre logs/scripts.
- El cambio de cron 16:00 fue **autorizado expresamente y verificado** con `crontab -l | grep ubuntu_cron_integrado` el 23/11. No debe volver a presentarse como propuesta pendiente.

## 6. Asistente IA: alcance y deuda funcional
- Worker Gemini + motor determinista + JSON del frontend. Se validaron cinco consultas funcionales después de correcciones; esto **no** demuestra capacidad de responder cualquier consulta libre.
- El usuario identificó como problema central que el asistente interpreta lenguaje natural, pero solo resuelve patrones/intenciones acotados. El objetivo de evolución es consultas amplias y fiables sobre datos reales, con identificación de cobertura, fuentes y límites; no sustituir esa meta por una FAQ sin decisión expresa.
- PRs, adaptadores y experimentos del asistente deben permanecer separados del ETL productivo.

## 7. Cómo continuar
1. Leer `docs/continuidad/README.md`, auditorías del 23/11, política maestra y esta memoria.
2. En la próxima corrida natural de 16:00, verificar log de extracción, carga MER, conciliación, publicación, commit y catálogo/Pages; cerrar P1 solo con evidencia completa.
3. En la próxima ejecución real de Compra Ágil nocturna o fin de semana, distinguir disparo, autorización de ventana, lotes, checkpoint, exportación, Pages y datos visibles; cerrar P3 solo con evidencia completa.
4. No reabrir P2 ni P4 salvo nueva evidencia. No solicitar nuevamente el listado de workflows ni la línea cron 16:00.
5. Ante nueva intervención, actualizar la memoria con fecha, evidencia, commit, estado y asuntos pendientes. Documentar explícitamente incertidumbres, especialmente estado de timers locales y diferencias entre snapshots.

## 8. Fuentes documentales
- `docs/continuidad/AUDITORIA_UBUNTU_2026-11-23.md`
- `docs/continuidad/AUDITORIA_GITHUB_ACTIONS_2026-11-23.md`
- `docs/continuidad/CONCILIACION_CRONOLOGICA_0900.md`
- `docs/continuidad/VALIDACION_ASISTENTE_GEMINI_2026-11-14.md`
- `docs/continuidad/INVENTARIO_PROCESOS.md`
- `docs/POLITICA_PROTECCION_CUATRO_PROCESOS.md`

**Seguridad documental:** no registrar tokens, secretos, datos personales ni logs íntegros sensibles. Esta memoria no autoriza cambios productivos.
