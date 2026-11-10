# Ruta B Compra Ágil — Tordo

**Estado:** piloto implementado en rama de desarrollo; no instalado ni activado en producción.

## Evidencia Ubuntu (10/11/2026)
2026-11-05: 514 códigos; 2026-11-06: 585; 2026-11-09: cero. Sin errores HTTP. Ninguna cifra acredita cobertura total de ChileCompra.

## Operación
```bash
python3 scripts/compra_agil_tordo_ruta_b.py --fecha 2026-11-05
python3 scripts/compra_agil_tordo_ruta_b.py --fecha 2026-11-06
python3 scripts/compra_agil_tordo_ruta_b.py --fecha 2026-11-09
```
Alternativamente, ejecutar manualmente el workflow `Compra Agil Tordo - piloto aislado` en la rama. **No hay schedule** ni credenciales.

El extractor pagina 100 registros, filtra `tipo_convocatoria=compra_agil`, ordena por fecha descendente, convierte fechas a `America/Santiago`, deduplica por código, comprueba el orden y detecta la fecha más reciente de Tordo. Se conservan SQLite, JSON de origen, CSV preliminar compatible con columnas Procesos del MER y reporte. Código de salida 0 = candidato; 2 = no apto; 1 = error. Una ejecución fallida no produce ninguna escritura a Sheets.

## Requisitos antes de activar ruta B productiva
1. Probar frescura de registros de noviembre posteriores al 6; distinguir atraso de catálogo y error de extracción.
2. Contrastar códigos y conteos con ZIP oficial de mes vencido o fuente independiente.
3. Validar equivalencia semántica de campos: monto_estimado de Tordo **no equivale automáticamente** a presupuesto oficial; no inventar ofertas ni resultados.
4. Preparar un adaptador separado de escritura MER con respaldo, lock compartido, deduplicación y rollback, y obtener aprobación expresa de activación.
5. Evaluar horarios de cron 09:00, 16:00, 16:15, 22:05 y timers mensuales; preservar cuatro procesos protegidos.
6. Verificar condiciones de reutilización de datos del tercero.

**Sin cambios en producción:** cron, API v2, MER, publicación y frontend intactos. Reversión: cerrar PR/eliminar rama.
