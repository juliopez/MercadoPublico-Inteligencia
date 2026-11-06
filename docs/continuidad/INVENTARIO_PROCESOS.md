# Inventario operativo de procesos y dependencias

**Corte documental:** 2026-11-06. **Autoridad principal:** [política de cuatro procesos](../POLITICA_PROTECCION_CUATRO_PROCESOS.md) y runbooks especializados.

| ID | Proceso | Activación documentada | Implementación / referencias | Salida y control |
|---|---|---|---|---|
| P1 | ETL licitaciones y OC | Ubuntu lun–vie 16:00 `America/Santiago` | [Línea base protegida](../LINEA_BASE_PROTEGIDA_CRON_1600.md) | MER, exportación y publicación; conteos y logs |
| P2 | API Compra Ágil incremental | Ubuntu 22:05 → `workflow_dispatch` GitHub Actions; lotes 400 | [Línea base 400](../LINEA_BASE_VALIDADA_API_COMPRA_AGIL_400.md), [disparador](../INSTALACION_DISPARADOR_API_GITHUB_UBUNTU.md) | Checkpoint, deduplicación, reintentos y publicación parcial |
| P3 | Rotación mensual | `mercadopublico-rotacion.timer` lun–vie 19:00, puerta último día hábil | [Inventario P3](../INVENTARIO_PROCESO_3_CAMBIO_MES.md); `deploy/systemd/mercadopublico-rotacion.timer`, `scripts/rotar_mes_operativo.py` | MER anterior a histórico, nuevo operativo y catálogo coherente |
| P4 | Conciliación oficial | `mercadopublico-conciliacion.timer` 10:00 diario y arranque; puerta día 10 hábil o posterior | [Inventario P4](../INVENTARIO_PROCESO_4_CONSOLIDACION_HISTORICA.md); `scripts/cierre_mensual_automatico.py` | Tres ZIP, seis tablas, respaldos, republicación, verificación remota |
| P5 | Publicación e índices | Dependiente de nuevas exportaciones/catálogo y workflows | [Mapa Actions](../GITHUB_ACTIONS_MANTENIMIENTO.md), [automatización](../AUTOMATIZACION.md) | Catálogo/fragmentos e índices sincronizados; Pages actualizado |
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
