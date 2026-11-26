# Historial de continuidad y decisiones

## 26/11/2026 — validación autónoma 09:00 y corrección del supervisor

Ubuntu: CONCILIACION_PUBLICADA 09:09:42, commit 64e939f8b. Publicador corregido ayer: run 45817071270 success, derivados e13ab616 09:12:32, períodos julio–noviembre; Pages run 45817690689 success. Catálogo noviembre 27.913 procesos. Se valida operación autónoma de la corrección b25ee1246. Supervisor separado run 45817542363/job 139901053600 falló 09:13:37 por guardia de período histórico, y su código también exigía exportación posterior a 16:00 fuera de contexto. Corrección autorizada c6567efb exclusivamente en verificar-publicacion-diaria-v2.yml: reconoce origen conciliación por metadatos Git (no autenticación criptográfica), revisa períodos afectados y operativo, analítica, fragmentos, búsqueda y perfiles de cuatro entidades; conserva bloqueo de históricos no reconocidos y control de frescura vespertino para schedule (y manual desde 18h). El control horario por sí solo no distingue una exportación API de una exportación ETL. No modifica cron, publicador, MER ni datos. Push propio activa verificación. Pendiente acreditar resultado del nuevo supervisor y control programado de tarde; no repetir conciliación. Reversión: revertir c6567efb previa autorización.


## Incidente 25/11/2026 — ETL 16:00, timeout TLS

Journal local aportado: cron inició 16:00:01 y cerró 16:03:05; despacho 16:15 inició 16:15:01 y cerró 16:15:05 (no acredita finalización remota). Logs arranque/orquestador 160001: descarga licitaciones iniciada, descarga OC falló en handshake TLS tras timeout 180 s, URLError, CONTROL_SINCRONIZACION FALLIDA, etapa principal exit 1, orquestador exit 10. Ambas fuentes se preparan antes de escrituras MER: no se alcanzaron carga, conciliación ni publicación. No se acreditó relación causal con túnel MCP.

Corrección autorizada `98d7e2e7`: únicamente descargar() de scripts/etl_zip_dos_fuentes.py; tres intentos por ZIP, pausas 30/60 s para errores transitorios de red/TLS y HTTP 408/429/500/502/503/504; timeout por operación de red 180 s intacto, limpieza .part, validación CSV/CRC y reemplazo atómico. No reintenta certificados inválidos ni errores de integridad. Guardas ETL intactas. Cambio en main, pendiente sincronización local y prueba de ejecución autónoma. No relanzar hoy sin autorización, especialmente mientras corre AUX-1615. Reversión: revertir commit de código en caso de regresión, previa autorización.


## Actualización vigente — 25/11/2026, recuperación de la conciliación 09:00

Incidente #91: publicador rechazó el último período exportado (octubre histórico). Corrección autorizada `b25ee1246` en publicacion-v2-post-etl.yml; reconoce conciliación y regenera derivados de períodos afectados, manteniendo guardas para otros orígenes. Commit de recuperación `2a3f7b4ae` a las 09:33:06 acredita publicación de derivados junio–noviembre. Captura del operador confirma frontend con 26.838 procesos de noviembre y fecha de publicación 25/11 09:12; coincide con catálogo, analítica y dimensión de Sheets menos encabezado. Incidente recuperado; siguiente conciliación natural debe acreditar funcionamiento sin intervención. No repetir conciliación ni reparación. La comparación de snapshots nocturno `bce75616b` y matinal `844dd7b7f` muestra noviembre 27.232 → 26.838 (-394), históricos +134 (junio +2, julio +2, agosto +5, septiembre +21, octubre +104), total -260. El conciliador conserva PK históricas existentes y retira del operativo solo tras verificar presencia en destino; los 260 son compatibles con deduplicación, no confirmados individualmente. No afirmar pérdida ni ausencia de pérdida sin cotejo por PK o evidencia local. Referencia: [runbook 09:00](CONCILIACION_CRONOLOGICA_0900.md). La mitigación de artefacto Pages del 24/11 (`a06fbfde`) es independiente; sin log de espera/reintentos no certificar su eficacia frente a nueva demora. P2/P4 de auditoría cerrados; P1 favorable con limitaciones locales y P3 nocturno/fin de semana en seguimiento. No confundir códigos de auditoría con IDs de inventario.


Este registro resume hitos relevantes; el historial Git conserva el detalle exacto. **No es un changelog exhaustivo de cada commit**.

| Fecha Chile | Hito | Evidencia / referencia |
|---|---|---|
| 2026-10-30 | Rotación octubre→noviembre corroborada | [Inventario P3](../INVENTARIO_PROCESO_3_CAMBIO_MES.md) |
| 2026-10-31 | Timer de conciliación instalado/habilitado según evidencia documentada | [Inventario P4](../INVENTARIO_PROCESO_4_CONSOLIDACION_HISTORICA.md) |
| 2026-11-04–06 | Disparador API Ubuntu 22:05 → Actions y lotes 400, confirmado operando por el responsable | [Política](../POLITICA_PROTECCION_CUATRO_PROCESOS.md), [disparador](../INSTALACION_DISPARADOR_API_GITHUB_UBUNTU.md) |
| 2026-11-06 | Seis secciones del frontend y barras de progreso funcionales, confirmadas por el responsable | `frontend-v2/` |
| 2026-11-06 | README principal didáctico, guías de instalación, arquitectura, UML y modelo ER publicados | [README](../../README.md), [Arquitectura](../ARQUITECTURA.md), [Modelo](../MODELO_DATOS.md) |
| 2026-11-06 | Mapa de GitHub Actions trasladado fuera de `.github/README.md` para liberar portada | [Mapa](../GITHUB_ACTIONS_MANTENIMIENTO.md) |
| 2026-11-06 | Se establece `docs/continuidad/` como entrada para nuevos chats | [Índice](README.md) |

## Registro obligatorio para cambios futuros

Añadir una fila con **fecha**, proceso afectado, motivo, autorización cuando corresponda, commit, prueba, resultado y procedimiento de reversión. Si solo se modificó documentación, indicarlo expresamente.

## Gobierno de cambios

La [política de cuatro procesos](../POLITICA_PROTECCION_CUATRO_PROCESOS.md) prevalece. No presentar una actualización documental como despliegue, instalación o prueba productiva.

| 2026-11-06, 16:22 Chile | Auditoría documental de solo lectura: commits de exportación e índices contrastados; runs de Actions y Ubuntu no accesibles; discrepancias registradas sin cambios productivos | [Auditoría](AUDITORIA_OPERATIVA.md), commits `0477f68` y `bc65f4f`; actualización documental `025aa635`, `6bafb6f` |

| 2026-11-10 | Cron 16:00 cargó MER, publicación falló por Sheets 429; recuperación por commit `cad2006aa`; Pages #371 timeout y #372 success | [Incidente V2](INCIDENTE_PUBLICACION_V2_2026-11-10.md) |
| 2026-11-10 | PR #10 fusionado a `main` (commit `676e9cf`): reintentos acotados de lectura Sheets, sin instalación Ubuntu verificada | [Incidente V2](INCIDENTE_PUBLICACION_V2_2026-11-10.md) |
| 2026-11-10 | PR #1 y #9 identificados como desarrollos experimentales, no productivos | [Iniciativas](INICIATIVAS_EN_DESARROLLO.md) |


## Actualización de evidencia Ubuntu — 10/11/2026, tarde

- `journalctl`: cron 16:00 inició a las 16:00:01; AUX-1615 inició 16:15:01 y cerró sesión 16:48:32 (Chile). El cierre de sesión no certifica por sí mismo éxito de cada etapa.
- `logs/licitaciones_api_1615.log`: 975 códigos únicos listados, 201 detalles guardados, 774 pendientes, 196 registros nuevos en MER, 0 modificados y 0 errores declarados; respaldo verificado y `CARGA_LICITACIONES_API_VERIFICADA`. El informe previo a la carga señalaba `escritura_mer:false` y `publicacion:false`, sin contradecir la carga posterior.
- La publicación automática de AUX-1615 terminó con `BLOQUEADO: cambios locales rastreados`. El `git status` posterior mostró únicamente archivos no rastreados; las comprobaciones de cambios rastreados y preparados dieron 0. **No se ha establecido la causa del estado distinto a las 16:48**; no atribuirlo a un defecto del script.
- A las 18:35:22 Chile el HEAD local fue `676e9cf` (PR #10, mitigación 429). La salida posterior de `git pull` durante la publicación manual avanzó hasta `d5b20cb37`; no confundir la mitigación 429 de P1/PUB-V2 con la causa del bloqueo de AUX-1615.
- Ejecución manual `bash scripts/ubuntu_publicar_v2_post_etl.sh --aplicar`: `EXPORTACION_V2_VERIFICADA`, 5.857 procesos de noviembre, 49.866 OC, 4.915 documentales MER, 2.111 nuevos y 6.326 vínculos publicados; commit `c8303ef3c` enviado a `main`, con `CATALOGO_PUBLICO_ACTUALIZADO`. **Esto acredita publicación en repositorio, no todavía éxito de Actions/Pages ni visibilidad individual de las 196 licitaciones**.
- Pendiente: verificar despliegue Pages y conciliación por identificadores de las 196; observar el siguiente ciclo autónomo 16:15 para comprobar que publica sin intervención. No repetir carga MER ni alterar procesos protegidos.

## Integración Gemini V2 — 14/11/2026

- **Autorización:** responsable aprobó continuar con pruebas, fusión, publicación y documentación del widget.
- **PR #15:** fusionado a `main` mediante commit `cfd5d85ef872a70bd3a85a4e56d4858c6792620b`.
- **Alcance:** sección 07 del frontend V2; integración del módulo UI existente con Cloudflare Worker `/chat`; pruebas de regresión del asistente y workflow independiente `.github/workflows/test-asistente-gemini.yml`.
- **Evidencia automatizada:** run GitHub Actions `43642073928`, workflow `Validar integración Gemini V2`, resultado `completed/success`, sobre commit `1fdf955616eb88ba39a1d6d01be88c219f43fec7`.
- **Publicación:** el archivo `frontend-v2/index.html` en `main` incluye la sección 07 y su script; **no se obtuvo confirmación HTTP del contenido servido por GitHub Pages ni prueba interactiva en navegador** en esta revisión. No declarar despliegue verificado hasta obtener esa evidencia.
- **Protección:** no se modificaron ETL, MER, cron, timers, Worker ni workflows operativos.
- **Reversión:** revertir el merge `cfd5d85` mediante PR de reversión, previa comprobación de cambios posteriores en `main`; no reescribir historia ni tocar datos.
