# Inventario operativo de procesos y dependencias

**Corte documental:** 2026-11-10. **Autoridad principal:** [política de cuatro procesos](../POLITICA_PROTECCION_CUATRO_PROCESOS.md) y runbooks especializados.

| ID | Proceso | Activación documentada | Implementación / referencias | Salida y control |
|---|---|---|---|---|
| P1 | ETL licitaciones y OC | Ubuntu lun–vie 16:00 `America/Santiago` | [Línea base protegida](../LINEA_BASE_PROTEGIDA_CRON_1600.md) | MER, exportación y publicación; conteos y logs |
| P2 | API Compra Ágil incremental | Ubuntu 22:05 → `workflow_dispatch` GitHub Actions; lotes 400 | [Línea base 400](../LINEA_BASE_VALIDADA_API_COMPRA_AGIL_400.md), [disparador](../INSTALACION_DISPARADOR_API_GITHUB_UBUNTU.md) | Checkpoint, deduplicación, reintentos y publicación parcial |
| P3 | Rotación mensual | `mercadopublico-rotacion.timer` lun–vie 19:00, puerta último día hábil | [Inventario P3](../INVENTARIO_PROCESO_3_CAMBIO_MES.md); `deploy/systemd/mercadopublico-rotacion.timer`, `scripts/rotar_mes_operativo.py` | MER anterior a histórico, nuevo operativo y catálogo coherente |
| P4 | Conciliación oficial | `mercadopublico-conciliacion.timer` 10:00 diario y arranque; puerta día 10 hábil o posterior | [Inventario P4](../INVENTARIO_PROCESO_4_CONSOLIDACION_HISTORICA.md); `scripts/cierre_mensual_automatico.py` | Tres ZIP, seis tablas, respaldos, republicación, verificación remota |
| P7 | Conciliación cronológica matinal | Ubuntu cron lun–vie 09:00; instalación confirmada 09/11, ejecución aún pendiente | [Runbook P7](CONCILIACION_CRONOLOGICA_0900.md); `scripts/ubuntu_conciliar_mer_0900.sh` | Redistribución por fecha propia, respaldo, verificación y exportación de períodos afectados; **no sustituye P4** |\n| P5 | Publicación e índices | Dependiente de nuevas exportaciones/catálogo y workflows | [Mapa Actions](../GITHUB_ACTIONS_MANTENIMIENTO.md), [automatización](../AUTOMATIZACION.md) | Catálogo/fragmentos e índices sincronizados; Pages actualizado |
| P6 | Consulta frontend | Navegador, demanda del usuario | `frontend-v2/`, `index.html` | Búsqueda, detalle, perfiles, comparaciones y guardados |

## Dependencias críticas compartidas

- `config/catalogo_sheets.json` y esquema MER de seis tablas.
- Google Sheets/Drive, permisos de cuenta de servicio y secretos privados.
- Bloqueo de escritura `logs/.mer_escritura_compartida.lock`.
- Publicación de cuatro entidades, fragmentos, catálogo e índices derivados.
- GitHub Actions, permisos de escritura y GitHub Pages.
- Zona horaria `America/Santiago` y feriados chilenos.

## Límites de la auditoría

Los archivos `deploy/systemd/` son **declaraciones versionadas**: para afirmar que un timer está activo en Ubuntu, comprobar `systemctl` y `journalctl` del equipo real. Para Actions, comprobar ejecuciones y artefactos, no solo el YAML. Para Pages, comprobar la respuesta HTTP y el contenido de catálogo/índices.

**No modificar procesos protegidos sin autorización expresa**, evaluación de impacto, respaldo, pruebas y reversión.


## Procesos auxiliares y cambios recientes

| Identificador | Función | Estado comprobado |
|---|---|---|
| AUX-1615 | Recuperación API licitaciones 16:15 lun–vie | Primera ejecución 10/11: 201 detalles y 196 nuevos MER; revisar logs en Ubuntu |
| PUB-V2 | Exportación Sheets → JSON → commit → Actions/Pages | Error 429 el 10/11; reintentos integrados en `main` por PR #10, sin instalación Ubuntu acreditada |
| EXP-01 | Escritor protegido Ofertas/Resultados | PR #1 abierto, no productivo |
| EXP-09 | Ruta B Tordo Compra Ágil | PR #9 abierto, no productivo |

Los auxiliares no sustituyen P1–P4. Ver [iniciativas](INICIATIVAS_EN_DESARROLLO.md).


## Actualización de evidencia Ubuntu — 10/11/2026, tarde

- `journalctl`: cron 16:00 inició a las 16:00:01; AUX-1615 inició 16:15:01 y cerró sesión 16:48:32 (Chile). El cierre de sesión no certifica por sí mismo éxito de cada etapa.
- `logs/licitaciones_api_1615.log`: 975 códigos únicos listados, 201 detalles guardados, 774 pendientes, 196 registros nuevos en MER, 0 modificados y 0 errores declarados; respaldo verificado y `CARGA_LICITACIONES_API_VERIFICADA`. El informe previo a la carga señalaba `escritura_mer:false` y `publicacion:false`, sin contradecir la carga posterior.
- La publicación automática de AUX-1615 terminó con `BLOQUEADO: cambios locales rastreados`. El `git status` posterior mostró únicamente archivos no rastreados; las comprobaciones de cambios rastreados y preparados dieron 0. **No se ha establecido la causa del estado distinto a las 16:48**; no atribuirlo a un defecto del script.
- A las 18:35:22 Chile el HEAD local fue `676e9cf` (PR #10, mitigación 429). La salida posterior de `git pull` durante la publicación manual avanzó hasta `d5b20cb37`; no confundir la mitigación 429 de P1/PUB-V2 con la causa del bloqueo de AUX-1615.
- Ejecución manual `bash scripts/ubuntu_publicar_v2_post_etl.sh --aplicar`: `EXPORTACION_V2_VERIFICADA`, 5.857 procesos de noviembre, 49.866 OC, 4.915 documentales MER, 2.111 nuevos y 6.326 vínculos publicados; commit `c8303ef3c` enviado a `main`, con `CATALOGO_PUBLICO_ACTUALIZADO`. **Esto acredita publicación en repositorio, no todavía éxito de Actions/Pages ni visibilidad individual de las 196 licitaciones**.
- Pendiente: verificar despliegue Pages y conciliación por identificadores de las 196; observar el siguiente ciclo autónomo 16:15 para comprobar que publica sin intervención. No repetir carga MER ni alterar procesos protegidos.
