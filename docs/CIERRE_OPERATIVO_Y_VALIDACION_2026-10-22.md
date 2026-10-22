# Cierre técnico y plan de validación — 22 de octubre de 2026

## Propósito
Conservar evidencia y estado exacto de la integración diaria Ubuntu → Google Sheets MER v2 → frontend V2 → GitHub Pages. Esta bitácora distingue instalación, simulación, escritura real, publicación y validación desatendida. Los horarios se expresan en America/Santiago.

## Evidencia reunida en Ubuntu (capturas del usuario)
- **21/10 16:00:** cron anterior ejecutado; `CARGA_VERIFICADA`, código 0. Lectura independiente del 22/10 comprobó 1.856 Procesos y 99.811 OC. En Procesos, 1.558 previos y 298 nuevas claves; discrepancia inicial de lectura resuelta.
- **22/10:** ZIP OC de octubre, 302.727 filas; extracción de 8.723 pares COT–OC desde `Descripcion/Obervaciones`.
- Consulta multimes de MER junio–octubre: 861 pares ya existentes, 5.339 sin COT presente, 2.523 elegibles con COT registrada y 8 OC ambiguas excluidas.
- Aplicación supervisada: 2.523 insertados y verificados en `MER_2026_10_OPERATIVO.VinculosCOT_OC`; estado `CONCILIACION_VERIFICADA` y respaldo local previo. Nueva simulación: 3.384 existentes y **0** pendientes, corroborando idempotencia.
- Cron Ubuntu reemplazado localmente: entrada `0 * * * * /bin/bash ".../scripts/ubuntu_cron_integrado.sh" --cron`. Filtro interno lunes a viernes 16:00. Se conservó respaldo de crontab y scripts anteriores.
- Exportadores en modo **simulación**: 1.856 Procesos, 99.811 OC. Exportación documental: 2.524 vínculos documentales encontrados en MER, 2.523 nuevos frente al JSON público preexistente, total proyectado 3.935. No equivalen a publicación.
- Prueba correctiva: se reparó la concatenación de dos comandos en `ubuntu_publicar_v2_post_etl.sh`. Se repitió simulación y terminó sin error.

## Código integrado (publicado, todavía sin ejecución automática integral verificada)
1. `scripts/ubuntu_cron_integrado.sh`: ETL original dos ZIP, conciliación incremental, invocación del publicador.
2. `scripts/etl_conciliacion_cot_oc.py`: fuente descriptiva OC, contraste multimes, deduplicación y respaldo.
3. `scripts/descargar_oc_incremental.py`: caché y verificación del ZIP OC.
4. `scripts/exportar_mer_operativo_v2.py`: Procesos y OC a fragmentos JSON públicos.
5. `scripts/exportar_vinculos_documentales_v2.py`: relaciones documentales, conservando las previamente publicadas y excluyendo ambigüedades.
6. `scripts/ubuntu_publicar_v2_post_etl.sh`: publicación vía Git **solo** tras sincronización exitosa y con autenticación adecuada.
7. `.github/workflows/publicacion-v2-post-etl.yml`: horario lógico 17:00 de Santiago, genera derivados y verifica conteos antes de commit.

### Cobertura y decisiones
- **Cron diario solo dos fuentes oficiales:** licitaciones y órdenes de compra. Compra Ágil NO dispone de ZIP diario garantizado; no descargarlo ni vaciar/modificar Ofertas/Resultados por ausencia de fuente.
- Históricos junio–septiembre inmutables. No reprocesar ni duplicar los 240.649 pares estructurados y 1.411 relaciones documentales verificadas previamente.
- El MER operativo conserva seis tablas. La publicación V2 usa fragmentos para Procesos/OC, vínculos documentales y derivados públicos; las tablas Ofertas y Resultados continúan sin alimentación diaria.
- **Tarea 5 — API Compra Ágil**: pendiente, separada del cron actual y de su puesta en marcha.
- No publicar credenciales, RUT privados, descripciones documentales extensas, ZIP históricos, respaldos ni bitácoras de Ubuntu.
- Mantener fuente, fecha y certeza de vínculos; la referencia documental NO prueba pago o adjudicación.

## Validación tras las 17:00 del 22/10 — palabra de inicio «valida»
1. **Ubuntu:** consultar `salida_operativa/estado_sincronizacion.json`, `salida_operativa/estado_conciliacion.json`, `logs/orquestador_integrado_*.log`; contrastar fecha, éxito, cambios y errores. Revisión local si el asistente no puede acceder.
2. **Google Sheets:** verificar conteos y la persistencia de nuevos vínculos sin alterar otras tablas ni las últimas marcas de éxito.
3. **GitHub:** confirmar commit de actualización del catálogo, partes de Procesos/OC y `vinculos-oc-verificados.json` del día; contrastar conteos, no solo hora de commit.
4. **Actions:** comprobar ejecución efectiva del workflow posterior, generación y conteo de `busqueda/`, `perfiles/`, `analitica/`, `indices/` y `relaciones-procesos/`; horarios UTC pueden cambiar por horario de verano.
5. **Pages y V2:** verificar recurso servido (no solo en rama `main`), contadores y códigos representativos, búsqueda transversal, «Ver detalle» y vínculos OC. Informar estados: aprobado, fallo concreto o pendiente por evidencia.
6. **Reintentos y recuperación:** comprobar que una falla de push/Actions no altere datos verificados en Sheets y que no se vuelva a insertar una PK existente. No ejecutar nuevas cargas históricas para auditar.

## Advertencias de cierre
- **No se acredita aún** una ejecución completa desatendida de Ubuntu 16:00 → GitHub 17:00 → Pages.
- El éxito de `git pull`, `bash -n` o una simulación **no acredita** push desatendido, despliegue ni validación visual.
- GitHub Actions programado se activa solo al detectarse exportación pública reciente. Si no ocurre, identificar si falló la carga, publicación Git o generación de derivados.
- El documento `PLAN_MEJORAS_CRON_1600_2026-10-21.md` es histórico: describía una propuesta anterior a la instalación del 22/10. No usarlo como estado vigente.

## Referencias
- `docs/CRON_INTEGRADO_UBUNTU_2026-10-22.md`
- `docs/PUBLICACION_MER_V2_POST_ETL_2026-10-22.md`
- `docs/ENRIQUECIMIENTO_OC_DESCRIPCIONES_2026-10-21.md`
- `docs/AUDITORIA_DIFERENCIAL_COT_OC_2026-10-21.md`

## Incidencia real del cron 16:00, observada a las 16:13 de Santiago
- El ETL actualizó MER operativo en Google Sheets (captura del registro local): Procesos 2.094, ÓrdenesCompra 108.269 en exportación; los conteos de carga incluyeron 8.458 OC nuevas, 8.426 modificadas, 814 proveedores nuevos.
- El publicador de Ubuntu falló en `scripts/exportar_mer_operativo_v2.py`, en `os.replace` desde `/tmp/export_mer_v2_*/procesos/2026-10/0003.json` hasta el repositorio, con `OSError: [Errno 18] Invalid cross-device link` (EXDEV). Mensaje local: `PUBLICACION_V2_FALLIDA`.
- Se corrigió la exportación mediante copia a archivo temporal **en el mismo directorio de destino** y reemplazo atómico local; commit `5f06d6aa`. **La corrección aún no se ha ejecutado ni verificado en Ubuntu**, por lo que no implica publicación automática exitosa hoy.
- La orquestación de las **17:00 se ejecuta en GitHub Actions**, no en Ubuntu. Su workflow `publicacion-v2-post-etl.yml` verifica un commit fresco en `catalogo-publico.json` o `vinculos-oc-verificados.json` posterior a las 16:00. Como la publicación Ubuntu falló antes de generar ese commit, puede concluir en modo `SIN_ORIGEN_FRESCO` sin actualizar los derivados; no darla por fallida ni por exitosa hasta examinar su ejecución y fuente.
- No volver a ejecutar el ETL de carga histórica ni alterar las hojas por este problema de publicación; cualquier reparación debe ser **solo de exportación** desde MER ya actualizado, con comprobaciones de integridad y sin escritura a Sheets. Mantener separados el publicador del MER y el workflow de derivados/Pages.

## Bitácora de control y traspaso a revisión de las 17:00 — 22/10/2026

### Línea de tiempo y nivel de evidencia
| Hora Chile | Evento | Evidencia y conclusión |
|---|---|---|
| 16:00:01 | Activación del cron integrado de Ubuntu | Archivo local `logs/orquestador_integrado_20261022_160001.log` mostrado por el usuario |
| 16:08 | Inspección del estado de carga | El estado de sincronización registra 8.458 OC nuevas, 8.426 modificadas y 90.832 sin cambios; 814 proveedores nuevos, 0 modificados y 19.292 sin cambios. No confirma por sí solo la conciliación |
| 16:13 | Inspección del log del orquestador | Exportación de MER operativo alcanzó 2.094 Procesos y 108.269 OC, seguida de `PUBLICACION_V2_FALLIDA` y `OSError [Errno 18] Invalid cross-device link` al trasladar fragmentos desde `/tmp` |
| Posterior a 16:13 | Corrección técnica publicada en GitHub | `scripts/exportar_mer_operativo_v2.py`, commit `5f06d6aa`: copia a temporal del mismo destino y `os.replace` local atómico; **no aplicada ni comprobada todavía en Ubuntu** |
| Posterior a 16:13 | Actualización de esta bitácora | Commit anterior `07396811` y registro del presente traspaso; no constituye ejecución de ETL |
| 17:00 (programado) | `.github/workflows/publicacion-v2-post-etl.yml` | Revisión pendiente; el disparador programado y sus resultados deberán confirmarse en GitHub Actions |

### Semántica operacional
1. **16:00, Ubuntu:** ETL de dos fuentes, persistencia MER en Sheets, conciliación COT–OC y exportación/publicación de fragmentos públicos. La prueba disponible confirma carga y error de publicación, pero no acredita por sí sola cierre correcto de todos los pasos.
2. **17:00, GitHub Actions:** workflow independiente, encargado de construir índices, perfiles y analítica **a partir de un catálogo y fragmentos publicados recientemente**. No descarga ZIP ni actualiza Sheets.
3. **Pages:** despliegue público independiente del éxito del workflow de derivados; validar siempre commit y contenido realmente servido.
4. **Compra Ágil / tarea 5:** sin API diaria en este ciclo; permanece en pausa por decisión expresa.

### Incidencia técnica y efecto esperado
El fallo `EXDEV` ocurrió **después** de operaciones de carga del MER y **antes** de generar el commit público esperado. En consecuencia, a las 17:00 GitHub Actions podría ejecutarse correctamente, pero omitir la generación por ausencia de una publicación fresca. Diferenciar **ejecución del workflow** de **actualización efectiva de datos**.

Los archivos locales parcialmente generados por una exportación interrumpida no se deben asumir coherentes. La recuperación debe regenerar íntegramente los fragmentos del mes operativo desde Sheets, comprobar catálogo, conteos y referencias de partes y solo entonces confirmar la publicación. No volver a ejecutar la carga del ETL ni repetir la escritura de Sheets para corregir este incidente.

### Protocolo acordado
El usuario regresará después de las 17:00 con el mensaje **«validar»**. En esa oportunidad:
- Consultar ejecución y logs del workflow de las 17:00, incluyendo paso `Comprobar exportacion nueva y hora de Santiago` y resultado `ready`.
- Verificar si existe un commit de **datos operativos** posterior a las 16:00 y si sus fragmentos y catálogo son coherentes. No confundir commits de código o documentación con exportación.
- Comprobar los 2.094 Procesos y 108.269 OC reportados en la simulación de exportación únicamente como referencia a contrastar con la publicación final.
- Comprobar vínculos documentales COT–OC, derivados, enlaces, índices y Pages; clasificar cada componente en **verificado**, **fallido** o **pendiente por falta de evidencia**.
- Si falta el origen público, proponer **solo recuperación de exportación**, con la corrección GitHub ya registrada, sin intervenir los históricos ni Sheets.

**Estado al cierre de esta bitácora:** ejecución Ubuntu con actualización de datos observada, publicación pública fallida, corrección documentada pero no instalada en Ubuntu, GitHub Actions 17:00 y Pages posteriores aún pendientes de comprobación.
