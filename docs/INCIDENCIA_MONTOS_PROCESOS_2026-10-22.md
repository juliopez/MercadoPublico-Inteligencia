# Incidencia de cobertura monetaria — MER octubre 2026

## Hallazgo
La analítica V2 de octubre contiene 2.094 registros de Procesos, 574 organismos distintos por nombre, 0 registros con importe válido y monto agregado 0. El fragmento público de octubre tiene `monto_disponible_clp` vacío para los procesos inspeccionados; el exportador MER conserva ese valor sin transformarlo. El problema es anterior a la agregación visual.

## Hipótesis a verificar
El importador `scripts/importador_historicos_v2.py::process_licitaciones` extrae el monto con `r.get("MontoDisponible")`. Si el archivo oficial de licitaciones utiliza otro encabezado, todos los montos quedan vacíos aunque el CSV incluya presupuestos. También es posible que la fuente no publique importes para ese corte. No asignar montos de órdenes de compra, estimaciones en otra moneda ni valores de adjudicación al campo de presupuesto: son magnitudes diferentes.

## Diagnóstico automatizado
El script `scripts/auditar_montos_licitaciones.py` lee temporalmente el ZIP público **2026-10** en memoria/disco temporal de Actions, inspecciona cabeceras monetarias, cantidad no vacía por campo y un ejemplo reducido, y produce un informe. No edita datos originales, Google Sheets, el ETL ni el catálogo público. Workflow: `.github/workflows/auditoria-montos-operativos.yml` (solo lectura), ejecución inicial solicitada el 22/10.

## Criterios antes de corregir
1. Confirmar nombre **exacto** y significado del campo disponible y su unidad monetaria (no mezclar CLP, UF o referencias).
2. Si existe un campo de presupuesto CLP compatible, corregir el mapeo de futuras cargas y preparar un enriquecimiento **idempotente por PK**, limitado a celdas monetarias actualmente vacías de octubre en `Procesos`. Previsualización y respaldo antes de escribir; no ejecutar el ETL completo ni tocar archivos históricos.
3. Si la fuente no posee ese dato, mantener el valor ausente y publicar una advertencia de cobertura. No reemplazar montos ausentes por cero.
4. Tras una corrección autorizada de MER operativo: exportar solo el mes operativo y regenerar sus derivados, validar `registros_con_monto` y `monto_total_clp`, verificar Pages.
5. Mantener la tarea 5 (API Compra Ágil) independiente de este análisis.

**Estado inicial:** causa exacta aún no confirmada; análisis programado. No declarar montos corregidos sin evidencia y revalidación.
