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
