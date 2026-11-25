# Inventario operativo de procesos y dependencias

## Actualización vigente — 25/11/2026, recuperación de la conciliación 09:00

Incidente #91: publicador rechazó el último período exportado (octubre histórico). Corrección autorizada `b25ee1246` en publicacion-v2-post-etl.yml; reconoce conciliación y regenera derivados de períodos afectados, manteniendo guardas para otros orígenes. Commit de recuperación `2a3f7b4ae` a las 09:33:06 acredita publicación de derivados junio–noviembre. Captura del operador confirma frontend con 26.838 procesos de noviembre y fecha de publicación 25/11 09:12; coincide con catálogo, analítica y dimensión de Sheets menos encabezado. Incidente recuperado; siguiente conciliación natural debe acreditar funcionamiento sin intervención. No repetir conciliación ni reparación. La comparación de snapshots nocturno `bce75616b` y matinal `844dd7b7f` muestra noviembre 27.232 → 26.838 (-394), históricos +134 (junio +2, julio +2, agosto +5, septiembre +21, octubre +104), total -260. El conciliador conserva PK históricas existentes y retira del operativo solo tras verificar presencia en destino; los 260 son compatibles con deduplicación, no confirmados individualmente. No afirmar pérdida ni ausencia de pérdida sin cotejo por PK o evidencia local. Referencia: [runbook 09:00](CONCILIACION_CRONOLOGICA_0900.md). La mitigación de artefacto Pages del 24/11 (`a06fbfde`) es independiente; sin log de espera/reintentos no certificar su eficacia frente a nueva demora. P2/P4 de auditoría cerrados; P1 favorable con limitaciones locales y P3 nocturno/fin de semana en seguimiento. No confundir códigos de auditoría con IDs de inventario.


**Corte documental:** 2026-11-25. **Autoridad principal:** [política de cuatro procesos](../POLITICA_PROTECCION_CUATRO_PROCESOS.md) y runbooks especializados.

| ID | Proceso | Activación documentada | Implementación / referencias | Salida y control |
|---|---|---|---|---|
| P1 | ETL licitaciones y OC | Ubuntu lun–vie 16:00 `America/Santiago`; cron exacto confirmado 23/11 | [Línea base protegida](../LINEA_BASE_PROTEGIDA_CRON_1600.md) | MER, exportación y publicación; conteos y logs |
| P2 | API Compra Ágil incremental | Ubuntu 22:05 → `workflow_dispatch` GitHub Actions; schedule UTC estacional de respaldo, ventana Chile; lotes 400 | [Línea base 400](../LINEA_BASE_VALIDADA_API_COMPRA_AGIL_400.md), [disparador](../INSTALACION_DISPARADOR_API_GITHUB_UBUNTU.md) | Checkpoint, deduplicación, reintentos y publicación parcial |
| P3 | Rotación mensual | `mercadopublico-rotacion.timer` lun–vie 19:00, puerta último día hábil | [Inventario P3](../INVENTARIO_PROCESO_3_CAMBIO_MES.md); `deploy/systemd/mercadopublico-rotacion.timer`, `scripts/rotar_mes_operativo.py` | MER anterior a histórico, nuevo operativo y catálogo coherente |
| P4 | Conciliación oficial | `mercadopublico-conciliacion.timer` 10:15 diario y arranque (horario documentado; última ejecución programada no acreditada); puerta día 10 hábil o posterior | [Inventario P4](../INVENTARIO_PROCESO_4_CONSOLIDACION_HISTORICA.md); `scripts/cierre_mensual_automatico.py` | Tres ZIP, seis tablas, respaldos, republicación, verificación remota |
| P7 | Conciliación cronológica matinal | Ubuntu cron lun–vie 09:00; runtime aislado desde 17/11; recuperación 25/11 confirmada | [Runbook P7](CONCILIACION_CRONOLOGICA_0900.md); `scripts/ubuntu_conciliar_mer_0900_aislado.sh` → `scripts/ubuntu_conciliar_mer_0900.sh` | Redistribución por fecha propia, respaldo, verificación y exportación de períodos afectados; **no sustituye P4** |
| P5 | Publicación e índices | Dependiente de nuevas exportaciones/catálogo y workflows | [Mapa Actions](../GITHUB_ACTIONS_MANTENIMIENTO.md), [automatización](../AUTOMATIZACION.md) | Catálogo/fragmentos e índices sincronizados; Pages actualizado |
| P6 | Consulta frontend | Navegador, demanda del usuario | `frontend-v2/`, `index.html` | Búsqueda, detalle, perfiles, comparaciones y guardados |

## Inventario de activaciones — corte documental 25/11

Se mantienen seis automatizaciones Ubuntu documentadas: cron 09:00, 16:00 y 16:15 (L–V); timers 10:15 cierre, 19:00 rotación y 22:05 despacho nocturno. Estado efectivo de timers no reconsultado hoy. Recuperación Compra Ágil sábado y domingo 20:00 Chile mediante Actions; validación de selector pendiente. Inventario Actions del 23/11: 74 YAML, seis con schedule, 68 sin schedule; todos los workflows devueltos por API activos. Las dos correcciones posteriores modificaron YAML existentes, no agregaron procesos ni horarios. No repetir censo salvo evidencia de cambio.

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
| AUX-1615 | Recuperación API licitaciones 16:15 lun–vie | Despacho remoto Ubuntu; 23/11 nueve lotes y 24/11 siete lotes registrados en GitHub; auditoría de seis jornadas previas cerrada |
| PUB-V2 | Exportación Sheets → JSON → commit → Actions/Pages | PR #26 reintentos 5xx instalado 23/11; mitigación Pages 24/11 y publicación multimes 25/11 implementadas |
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
