# Historial de continuidad y decisiones

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
