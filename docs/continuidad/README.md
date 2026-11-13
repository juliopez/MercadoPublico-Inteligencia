## Cierre operativo 12/11/2026 — disparos Ubuntu y ejecución GitHub

**Configuración confirmada por salida de terminal del usuario:** el instalador `scripts/instalar_cron_licitaciones_1615.sh` informó `CRON_INSTALADO` y mostró la entrada `15 16 * * 1-5` invocando `scripts/ubuntu_dispatch_licitaciones_1615.sh`. El cron anterior de recuperación local 16:15 fue sustituido por el disparador remoto. GitHub Actions contiene `.github/workflows/licitaciones-api-1615-actions.yml` en `main` y usa únicamente `workflow_dispatch`, sin horario `schedule` de GitHub. PR #13 fusionado. **No hay todavía evidencia de ejecución remota exitosa ni de publicación final en Pages para el nuevo proceso**.

**Los cuatro procesos dependen de que Ubuntu esté encendido al momento del disparo**, en horario de Chile y de lunes a viernes:

| Hora | Proceso | Dónde se ejecuta |
| --- | --- | --- |
| 09:00 | P7 conciliación cronológica MER | Ubuntu, proceso completo |
| 16:00 | P1 ETL ZIP licitaciones y OC | Ubuntu, proceso completo |
| 16:15 | AUX licitaciones API | Ubuntu dispara GitHub Actions; ejecución remota |
| 22:05 | P2 Compra Ágil API | Ubuntu dispara GitHub Actions; ejecución remota |

Una vez aceptado el disparo de las 16:15 o 22:05, el procesamiento remoto no necesita que Ubuntu permanezca encendido. El disparo de las 22:05 requiere que el temporizador local esté activo; su estado efectivo no queda acreditado por la instalación del cron 16:15.

**Primera comprobación pendiente 13/11:** verificar que el disparo 16:15 aparezca en Actions, que termine correctamente, que MER se actualice, que los derivados se publiquen y que el frontend muestre los datos. Conservar registro de errores sin presumir éxito. El cron 16:00 y los demás procesos no fueron modificados por el instalador 16:15.

# Punto de recuperación operativa — Observatorio de Mercado Público

**Última revisión documental:** 2026-11-11 (Chile). **Repositorio:** `juliopez/MercadoPublico-Inteligencia`, rama principal `main`.

**Actualización 11/11/2026:** [Incidente P7 09:00, recuperación P1/AUX y excepción Compra Ágil nocturna](INCIDENTE_CONCILIACION_2026-11-11.md). AUX-1615 finalizó 22:37:38 con cero pendientes y publicación en GitHub; workflows posteriores exitosos. El workflow remoto Compra Ágil #26 quedó en ejecución (última captura 22:54). **Pendiente 12/11:** validar P7 09:00, comprobar resultado nocturno y **reactivar el temporizador de usuario** `mercadopublico-api-github-dispatch.timer` para las 22:05. No afirmar que esté reactivado. Esta actualización prevalece sobre las previsiones históricas de primera ejecución que figuran más abajo.

> **Empezar aquí al abrir un nuevo chat.** Esta carpeta es el índice de continuidad; no reemplaza el código, los logs Ubuntu, los resultados de GitHub Actions ni la documentación protegida. Las afirmaciones de ejecución requieren evidencia reciente.

## Incidente publicación V2 del 10/11/2026 — mitigación incorporada a main

Consultar [INCIDENTE_PUBLICACION_V2_2026-11-10.md](INCIDENTE_PUBLICACION_V2_2026-11-10.md). Carga MER 16:02 verificada; publicador bloqueado por cuota Sheets 429; recuperación GitHub commit `cad2006aa`, Pages #371 timeout y #372 success; frontend actualizado. El PR #10 fue fusionado en `main` (commit `676e9cf4425cea95462b5d493be579801dadf3ab`): reintentos de lectura Sheets ante 429. **La instalación en Ubuntu depende de ejecutar `git pull --ff-only origin main`; no hay confirmación de esa actualización local.** No declarar automatización desatendida hasta validar recuperación de fallas y publicación final.

## Desarrollos experimentales abiertos

- [PR #1 — escritor protegido de Ofertas/Resultados](https://github.com/juliopez/MercadoPublico-Inteligencia/pull/1): pruebas aisladas con copia MER, sin API ni escritura operativa; falta CI/ensayo y rollback ante fallo parcial.
- [PR #9 — Ruta B Compra Ágil con Tordo](https://github.com/juliopez/MercadoPublico-Inteligencia/pull/9): piloto de extracción y staging, sin cron ni MER productivo; falta validar frescura, cobertura y semántica.
- [Registro de iniciativas](INICIATIVAS_EN_DESARROLLO.md): alcance, estado y condiciones para decidir integración.

## Incidente P4 del 10/11/2026 — cierre octubre recuperado

**Leer primero:** [INCIDENTE_CIERRE_2026-10_2026-11-10.md](INCIDENTE_CIERRE_2026-10_2026-11-10.md). La publicación histórica y la recuperación supervisada de octubre quedaron verificadas; la puerta devolvió `COMPLETADO` / `NINGUNA`. El timer Ubuntu fue reprogramado localmente a **10:15 America/Santiago**; la captura confirma la programación, una ejecución correcta a las 10:06 y **el disparo automático de las 10:15:54 con resultado `COMPLETADO` / `NINGUNA`**. No confundir recuperación manual con validación integral de automatización futura. No repetir carga ni publicación de octubre.

## Lectura obligatoria y orden

1. [ESTADO_ACTUAL.md](ESTADO_ACTUAL.md): qué sabemos, qué está pendiente y qué no se debe afirmar.
2. [INVENTARIO_PROCESOS.md](INVENTARIO_PROCESOS.md): disparadores, archivos, dependencias, controles y runbooks.
3. [AUDITORIA_OPERATIVA.md](AUDITORIA_OPERATIVA.md): evidencia documentada y protocolo de auditoría.
4. [INCIDENCIAS_PENDIENTES.md](INCIDENCIAS_PENDIENTES.md): riesgos abiertos y criterios de cierre.
5. [HISTORIAL_CAMBIOS.md](HISTORIAL_CAMBIOS.md): decisiones, cambios relevantes y referencias.
6. [Política maestra de protección](../POLITICA_PROTECCION_CUATRO_PROCESOS.md): **prevalece ante cualquier resumen**.

## Nuevo proceso: conciliación cronológica matinal 09:00 (2026-11-09)

**Documento operativo:** [CONCILIACION_CRONOLOGICA_0900.md](CONCILIACION_CRONOLOGICA_0900.md). El usuario confirmó con captura de `crontab -l` la entrada `0 9 * * 1-5` y etiqueta `MER_CONCILIACION_0900` en Ubuntu. El cron está **instalado**, pero su primera ejecución está prevista para **martes 10/11/2026, 09:00 Chile** y **no ha sido validada**. Clasifica por fecha propia las hojas Procesos, OrdenesCompra, Ofertas y Resultados; deja Proveedores y VinculosCOT_OC sin traslado automático. Respalda, escribe en MER histórico, verifica, retira del operativo y exporta los períodos afectados. **Es distinto del proceso P4 de conciliación oficial del mes vencido**.

## Hito operativo: cron de licitaciones API 16:15 (2026-11-09)

**Evidencia:** salida de terminal Ubuntu aportada el 9 de noviembre de 2026: `git pull --ff-only origin main` completado hasta `e643fa688`; `bash scripts/instalar_cron_licitaciones_1615.sh` informó `CRON_INSTALADO`; `crontab -l | grep MER_LICITACIONES_API_1615` confirmó la entrada `15 16 * * 1-5`. Huso horario local validado por el instalador: `America/Santiago`.

**Estado:** código actualizado, cron **instalado y programado**; **sin evidencia todavía de ejecución productiva, carga MER ni publicación V2**. Primera ejecución prevista: **martes 10 de noviembre de 2026, 16:15 (Chile)**.

**Contrato aprobado:** consultar el listado API del **día de ejecución** y recuperar **todos** sus códigos, incluso cuando la publicación original corresponda a octubre u otro mes. Sin cuota diaria de 400. Procesar en lotes de 200 detalles, con pausa API, reintentos y checkpoint SQLite. Cargar registros nuevos en **Procesos del MER operativo vigente**, sin alterar los MER históricos y conservando fecha original. Respaldar/verificar la escritura y publicar V2 después de cada lote. La tarea es independiente de cron 16:00 y Compra Ágil nocturna.

**Archivos:** `scripts/ubuntu_recuperar_licitaciones_1615.sh`, `scripts/recuperar_licitaciones_api.py`, `scripts/cargar_licitaciones_api_mer.py`, `scripts/instalar_cron_licitaciones_1615.sh`, `deploy/cron/licitaciones-api-1615.example`.

**Primera auditoría (10/11):** contrastar listado y códigos únicos del día, detalles recuperados/fallidos, checkpoint, respaldo y lectura posterior MER, resultado de publicación, duración, locks y convivencia con otros procesos. Consultar `logs/licitaciones_api_1615.log` en Ubuntu. No confundir instalación exitosa con ejecución exitosa.

## Línea base API de licitaciones — 1 al 9 de noviembre de 2026

Consulta manual de solo lectura ejecutada en Ubuntu el **09/11/2026**, contra `/servicios/v1/publico/licitaciones.json?fecha=DDMMYYYY`. Las primeras consultas tuvieron errores HTTP 429 por falta de pausa; se repitieron únicamente los días 2, 6 y 7 con espera y reintentos. La tabla recoge **nueve respuestas exitosas** y el campo `Cantidad` de cada respuesta.

| Fecha | Cantidad API | Acumulado |
|---|---:|---:|
| 2026-11-01 | 6 | 6 |
| 2026-11-02 | 1.469 | 1.475 |
| 2026-11-03 | 1.149 | 2.624 |
| 2026-11-04 | 1.169 | 3.793 |
| 2026-11-05 | 1.295 | 5.088 |
| 2026-11-06 | 1.385 | 6.473 |
| 2026-11-07 | 29 | 6.502 |
| 2026-11-08 | 3 | 6.505 |
| 2026-11-09 | 1.697 | **8.202** |

**Interpretación:** 8.202 es la suma de cantidades diarias, **no un conteo de códigos únicos ni necesariamente de licitaciones publicadas en noviembre**. Una consulta anterior reportó 8.165 entradas y 8.124 códigos únicos; existe una diferencia de 37 entradas entre mediciones que requiere cotejo de listados/códigos, no suposición de equivalencia. Esta línea base sirve para contrastar la ejecución del cron del 10/11; no demuestra por sí sola carga al MER.

## Cómo reanudar una auditoría

1. Leer estos documentos y la política maestra.
2. Inspeccionar el **estado real** de `main`, workflows, últimos runs, scripts, catálogo y artefactos públicos.
3. Solicitar o revisar evidencia de Ubuntu cuando no esté disponible desde GitHub (timers, `journalctl`, cron, logs, checkpoints). **No inferir el estado de Ubuntu a partir del código**.
4. Distinguir `documentado`, `implementado`, `instalado`, `ejecutado`, `validado` y `pendiente`.
5. Auditar en orden: cron 16:00 → disparador/API nocturna → rotación → conciliación → publicación → índices → frontend.
6. Proponer correcciones solo ante problemas verificados. **No modificar** ETL, API, timers, locks, workflows productivos ni contratos sin autorización expresa y análisis de impacto.
7. Al finalizar, actualizar estado, auditoría, incidencias e historial **solo con evidencia obtenida**, incluyendo fecha, commit y resultados.

## Prompt para una conversación nueva

> Continuemos la auditoría operativa del Observatorio de Mercado Público, repositorio `juliopez/MercadoPublico-Inteligencia`. Lee primero `docs/continuidad/README.md`, sus cinco documentos vinculados y `docs/POLITICA_PROTECCION_CUATRO_PROCESOS.md`. Contrasta el estado documentado con el código y las últimas ejecuciones de GitHub Actions; para Ubuntu, identifica qué evidencia local falta. Audita cron, API nocturna, rotación, conciliación, publicación e índices. No modifiques procesos protegidos sin mi aprobación expresa. Al cerrar, actualiza la documentación de continuidad.

## Documentación pública y técnica

- [README principal](../../README.md) · [Arquitectura](../ARQUITECTURA.md) · [Modelo de datos](../MODELO_DATOS.md).
- [Operación](../OPERACION.md) · [Automatización](../AUTOMATIZACION.md) · [Índice documental completo](../INDICE_DOCUMENTACION.md).
- [Mapa de workflows](../GITHUB_ACTIONS_MANTENIMIENTO.md).

**Nota de alcance:** esta carpeta está en un repositorio público. No incluir secretos, tokens, rutas locales sensibles, identificadores privados ni logs con datos personales.


## Actualización de evidencia Ubuntu — 10/11/2026, tarde

- `journalctl`: cron 16:00 inició a las 16:00:01; AUX-1615 inició 16:15:01 y cerró sesión 16:48:32 (Chile). El cierre de sesión no certifica por sí mismo éxito de cada etapa.
- `logs/licitaciones_api_1615.log`: 975 códigos únicos listados, 201 detalles guardados, 774 pendientes, 196 registros nuevos en MER, 0 modificados y 0 errores declarados; respaldo verificado y `CARGA_LICITACIONES_API_VERIFICADA`. El informe previo a la carga señalaba `escritura_mer:false` y `publicacion:false`, sin contradecir la carga posterior.
- La publicación automática de AUX-1615 terminó con `BLOQUEADO: cambios locales rastreados`. El `git status` posterior mostró únicamente archivos no rastreados; las comprobaciones de cambios rastreados y preparados dieron 0. **No se ha establecido la causa del estado distinto a las 16:48**; no atribuirlo a un defecto del script.
- A las 18:35:22 Chile el HEAD local fue `676e9cf` (PR #10, mitigación 429). La salida posterior de `git pull` durante la publicación manual avanzó hasta `d5b20cb37`; no confundir la mitigación 429 de P1/PUB-V2 con la causa del bloqueo de AUX-1615.
- Ejecución manual `bash scripts/ubuntu_publicar_v2_post_etl.sh --aplicar`: `EXPORTACION_V2_VERIFICADA`, 5.857 procesos de noviembre, 49.866 OC, 4.915 documentales MER, 2.111 nuevos y 6.326 vínculos publicados; commit `c8303ef3c` enviado a `main`, con `CATALOGO_PUBLICO_ACTUALIZADO`. **Esto acredita publicación en repositorio, no todavía éxito de Actions/Pages ni visibilidad individual de las 196 licitaciones**.
- Pendiente: verificar despliegue Pages y conciliación por identificadores de las 196; observar el siguiente ciclo autónomo 16:15 para comprobar que publica sin intervención. No repetir carga MER ni alterar procesos protegidos.
