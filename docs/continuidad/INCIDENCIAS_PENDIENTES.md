# Pendientes y riesgos operativos

## 27/11/2026 — recurrencia de disponibilidad transitoria del artefacto Pages

Run 46082016750/job 140783378577: carga exitosa 20:24:51.836, artefacto 15237394082 (320999505 bytes), API Actions disponible 20:24:52.275, deploy-pages encontró cero artefactos 20:24:52.632. Consulta posterior confirma artefacto existente y no expirado. La mitigación a06fbfde por consulta REST sola fue insuficiente; hipótesis de propagación inconsistente entre APIs, no causa interna confirmada. Run previo 46081915368 del mismo SHA e7271d7e1 verificó despliegue y catálogo público; noviembre 29.622 procesos y 158.363 OC según catálogo Git. No repetir ETL ni carga MER.

Corrección autorizada 68d102bb exclusivamente en .github/workflows/preview-frontend-v2.yml: conserva verificación REST previa, espera adicional 30 s, hasta tres invocaciones deploy-pages sobre mismo artefacto (esperas 30/60 s tras fallos); dos primeras toleran error solo para permitir reintento; tercera falla explícitamente si no logra desplegar, guardia de éxito y comprobación pública sin caché intactas. URL de entorno admite salida de cualquiera de tres intentos; timeout job 20→30 min. Sin cambios en horarios, grupos de concurrencia, ETL, datos o Sheets. Push activa workflow. Pendiente validar ejecución corregida y recuperación real ante nuevo fallo transitorio; no se garantiza recuperación frente a fallos persistentes. Reversión: revertir 68d102bb previa autorización.


## 26/11/2026 — colisión de publicación vespertina

ETL 16:00 terminó ORQUESTADOR OK 16:27:16, exportación 36ff8cdab: noviembre 27.917 procesos, 150.166 OC, 467 ofertas, 43 resultados. Run 45883764460/job 140129262208 validó derivados pero push rechazado 16:28:20 (main esperado b358e9386, real 090c6dfb), tras publicaciones concurrentes de participación y analítica. Pages run 45883873342 exitoso, pero búsqueda/perfiles del repositorio quedaron con 27.913 procesos y 118.574 OC; diferencias 4 y 31.592. API 16:15 run 45882218904 en curso al auditar. Supervisor matinal corregido run 45820050042 success.

Corrección autorizada ce718522: exclusivamente .github/workflows/publicacion-v2-post-etl.yml. Hasta cinco intentos de push; cada intento obtiene main remoto, regenera y valida derivados, preserva períodos autorizados acumulados, sin rebase de derivados obsoletos ni force push. Esperas 10/20/30/40 s; agotamiento explícito; errores de validación mantienen bloqueo. Reset hard únicamente en checkout efímero del runner. Push de workflow dispara recuperación de índices sin repetir ETL ni escribir Sheets. Se conserva horario y grupo de concurrencia. Pendiente confirmar ejecución corregida y coherencia catálogo/búsqueda/perfiles/Pages; no se garantiza ausencia de colisiones futuras ni recuperación ante fallos persistentes. Reversión: revertir ce718522 previa autorización.


## 26/11/2026 — validación autónoma 09:00 y corrección del supervisor

Ubuntu: CONCILIACION_PUBLICADA 09:09:42, commit 64e939f8b. Publicador corregido ayer: run 45817071270 success, derivados e13ab616 09:12:32, períodos julio–noviembre; Pages run 45817690689 success. Catálogo noviembre 27.913 procesos. Se valida operación autónoma de la corrección b25ee1246. Supervisor separado run 45817542363/job 139901053600 falló 09:13:37 por guardia de período histórico, y su código también exigía exportación posterior a 16:00 fuera de contexto. Corrección autorizada c6567efb exclusivamente en verificar-publicacion-diaria-v2.yml: reconoce origen conciliación por metadatos Git (no autenticación criptográfica), revisa períodos afectados y operativo, analítica, fragmentos, búsqueda y perfiles de cuatro entidades; conserva bloqueo de históricos no reconocidos y control de frescura vespertino para schedule (y manual desde 18h). El control horario por sí solo no distingue una exportación API de una exportación ETL. No modifica cron, publicador, MER ni datos. Push propio activa verificación. Pendiente acreditar resultado del nuevo supervisor y control programado de tarde; no repetir conciliación. Reversión: revertir c6567efb previa autorización.


## Incidente 25/11/2026 — ETL 16:00, timeout TLS

Journal local aportado: cron inició 16:00:01 y cerró 16:03:05; despacho 16:15 inició 16:15:01 y cerró 16:15:05 (no acredita finalización remota). Logs arranque/orquestador 160001: descarga licitaciones iniciada, descarga OC falló en handshake TLS tras timeout 180 s, URLError, CONTROL_SINCRONIZACION FALLIDA, etapa principal exit 1, orquestador exit 10. Ambas fuentes se preparan antes de escrituras MER: no se alcanzaron carga, conciliación ni publicación. No se acreditó relación causal con túnel MCP.

Corrección autorizada `98d7e2e7`: únicamente descargar() de scripts/etl_zip_dos_fuentes.py; tres intentos por ZIP, pausas 30/60 s para errores transitorios de red/TLS y HTTP 408/429/500/502/503/504; timeout por operación de red 180 s intacto, limpieza .part, validación CSV/CRC y reemplazo atómico. No reintenta certificados inválidos ni errores de integridad. Guardas ETL intactas. Cambio en main, pendiente sincronización local y prueba de ejecución autónoma. No relanzar hoy sin autorización, especialmente mientras corre AUX-1615. Reversión: revertir commit de código en caso de regresión, previa autorización.


## Actualización vigente — 25/11/2026, recuperación de la conciliación 09:00

Incidente #91: publicador rechazó el último período exportado (octubre histórico). Corrección autorizada `b25ee1246` en publicacion-v2-post-etl.yml; reconoce conciliación y regenera derivados de períodos afectados, manteniendo guardas para otros orígenes. Commit de recuperación `2a3f7b4ae` a las 09:33:06 acredita publicación de derivados junio–noviembre. Captura del operador confirma frontend con 26.838 procesos de noviembre y fecha de publicación 25/11 09:12; coincide con catálogo, analítica y dimensión de Sheets menos encabezado. Incidente recuperado; siguiente conciliación natural debe acreditar funcionamiento sin intervención. No repetir conciliación ni reparación. La comparación de snapshots nocturno `bce75616b` y matinal `844dd7b7f` muestra noviembre 27.232 → 26.838 (-394), históricos +134 (junio +2, julio +2, agosto +5, septiembre +21, octubre +104), total -260. El conciliador conserva PK históricas existentes y retira del operativo solo tras verificar presencia en destino; los 260 son compatibles con deduplicación, no confirmados individualmente. No afirmar pérdida ni ausencia de pérdida sin cotejo por PK o evidencia local. Referencia: [runbook 09:00](CONCILIACION_CRONOLOGICA_0900.md). La mitigación de artefacto Pages del 24/11 (`a06fbfde`) es independiente; sin log de espera/reintentos no certificar su eficacia frente a nueva demora. P2/P4 de auditoría cerrados; P1 favorable con limitaciones locales y P3 nocturno/fin de semana en seguimiento. No confundir códigos de auditoría con IDs de inventario.


## Actualización vigente — 24/11/2026

[Incidente Pages, evidencia y corrección preventiva](AUDITORIA_GITHUB_ACTIONS_2026-11-23.md#actualización-24112026--incidente-pages-y-mitigación-preventiva-p3-de-auditoría): Compra Ágil nocturna del 23/11 publicó cuatro lotes (1.600 registros adicionales) en MER y GitHub, pero falló el despliegue por ausencia momentánea del artefacto recién cargado. Mitigación en `a06fbfde`: comprobar disponibilidad del artefacto antes del despliegue (12 intentos, intervalo 10 s). Frontend recuperado según captura del operador: 25.002 procesos en noviembre, fecha 24/11 03:15; coincide con el total de Sheets. **Incidente recuperado, prevención pendiente de validación autónoma; P3 de auditoría sigue en seguimiento**, incluida recuperación de fin de semana. P1 favorable con limitaciones de evidencia local; P2/P4 cerrados. Esta actualización prevalece sobre estados anteriores de auditoría, no cambia los identificadores de procesos históricos. Sin nuevas modificaciones productivas.


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


## Actualización de evidencia Ubuntu — 10/11/2026, tarde

- `journalctl`: cron 16:00 inició a las 16:00:01; AUX-1615 inició 16:15:01 y cerró sesión 16:48:32 (Chile). El cierre de sesión no certifica por sí mismo éxito de cada etapa.
- `logs/licitaciones_api_1615.log`: 975 códigos únicos listados, 201 detalles guardados, 774 pendientes, 196 registros nuevos en MER, 0 modificados y 0 errores declarados; respaldo verificado y `CARGA_LICITACIONES_API_VERIFICADA`. El informe previo a la carga señalaba `escritura_mer:false` y `publicacion:false`, sin contradecir la carga posterior.
- La publicación automática de AUX-1615 terminó con `BLOQUEADO: cambios locales rastreados`. El `git status` posterior mostró únicamente archivos no rastreados; las comprobaciones de cambios rastreados y preparados dieron 0. **No se ha establecido la causa del estado distinto a las 16:48**; no atribuirlo a un defecto del script.
- A las 18:35:22 Chile el HEAD local fue `676e9cf` (PR #10, mitigación 429). La salida posterior de `git pull` durante la publicación manual avanzó hasta `d5b20cb37`; no confundir la mitigación 429 de P1/PUB-V2 con la causa del bloqueo de AUX-1615.
- Ejecución manual `bash scripts/ubuntu_publicar_v2_post_etl.sh --aplicar`: `EXPORTACION_V2_VERIFICADA`, 5.857 procesos de noviembre, 49.866 OC, 4.915 documentales MER, 2.111 nuevos y 6.326 vínculos publicados; commit `c8303ef3c` enviado a `main`, con `CATALOGO_PUBLICO_ACTUALIZADO`. **Esto acredita publicación en repositorio, no todavía éxito de Actions/Pages ni visibilidad individual de las 196 licitaciones**.
- Pendiente: verificar despliegue Pages y conciliación por identificadores de las 196; observar el siguiente ciclo autónomo 16:15 para comprobar que publica sin intervención. No repetir carga MER ni alterar procesos protegidos.
