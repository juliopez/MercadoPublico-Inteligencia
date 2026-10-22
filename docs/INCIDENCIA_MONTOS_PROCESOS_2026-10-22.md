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

## Diagnóstico confirmado (auditoría oficial 22/10)
GitHub Actions `Auditoria montos licitaciones operativas` ejecutó lectura real del ZIP público 2026-10. Se confirmó que el CSV no tiene `MontoDisponible`; sí contiene `MontoEstimado`, `CodigoMoneda`, `Estimacion` y `VisibilidadMonto`. El origen incluye montos en CLP, USD y CLF; `Estimacion` distingue 1 (presupuesto disponible) y 2 (precio referencial). Por lo tanto, leer indiscriminadamente `MontoEstimado` sería incorrecto.

**Corrección futura publicada:** `scripts/importador_historicos_v2.py` ahora utiliza `monto_presupuesto_clp(row)`, que toma `MontoEstimado` solo con `CodigoMoneda=CLP`, `Estimacion=1` y `VisibilidadMonto=1`. Los otros casos quedan vacíos deliberadamente. No se ejecutó el ETL de carga.

**Recuperación controlada de octubre preparada:** `scripts/completar_montos_operativos.py` reconstruye presupuestos por código desde el ZIP mensual público y compara solo `Procesos.monto_disponible_clp` del MER vigente. En modo predeterminado simula sin escribir; `--aplicar` realiza copia CSV local completa de la hoja, actualiza **solo celdas vacías**, excluye claves ambiguas y montos en otra moneda, preserva todos los valores existentes y verifica lectura posterior. No edita los ZIP ni las hojas históricas ni otras pestañas.

**Pendiente de ejecución local:** el script requiere credencial de servicio accesible únicamente en Ubuntu. Aquí no se ejecutó ninguna escritura al MER y no se debe afirmar que los montos ya se recuperaron. Se debe inspeccionar el reporte de simulación antes de la aplicación. Tras una aplicación verificada: ejecutar solo `ubuntu_publicar_v2_post_etl.sh --aplicar` (sin repetir ETL), luego `publicacion-v2-post-etl.yml` para recalcular analítica y desplegar Pages.

### Comandos Ubuntu
```bash
cd "$HOME/Julio Lopez/chilecompra/MercadoPublico-Inteligencia" || exit 1
git pull --ff-only origin main
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/mercadopublico/servicio-google.json"
.venv/bin/python scripts/completar_montos_operativos.py
# Revisar conteos, ambigüedades y celdas propuestas antes de aplicar:
.venv/bin/python scripts/completar_montos_operativos.py --aplicar
```
No ejecutar la carga histórica ni la actualización ETL completa. Los valores marcados como **precio referencial** no se deben sumar como presupuestos disponibles.

## Recuperación aplicada en Ubuntu — 22/10/2026, 18:15 Chile
Captura de ejecución entregada por el usuario: `scripts/completar_montos_operativos.py --aplicar` reportó 2.094 filas MER, 794 celdas monetarias a completar, 1.300 sin presupuesto CLP visible, 0 ambigüedades, generó respaldo local `salida_operativa/respaldo_montos_procesos_2026-10_20261022_181505.csv` y terminó con `MONTOS_OPERATIVOS_COMPLETADOS_Y_VERIFICADOS 794`. Esto verifica la corrección en Google Sheets, **no** su reflejo todavía en JSON/Pages. El respaldo y credenciales permanecen exclusivamente en Ubuntu; no subirlos a GitHub. Próximos pasos: republicar solo MER operativo desde Sheets (`scripts/ubuntu_publicar_v2_post_etl.sh --aplicar`), activar generación de derivados V2 con workflow `publicacion-v2-post-etl.yml`, confirmar conteos de 2.094 Procesos y 794 `registros_con_monto` en analítica, cotejar montos y Pages. Nunca repetir el ETL de carga para esta recuperación.

## Cierre de generación y enlace de despliegue — 22/10, 18:45 Chile
- El workflow manual `Publicacion V2 posterior al ETL Ubuntu #2` (run 39856729674) finalizó satisfactoriamente. El JSON `frontend-v2/data/analitica/2026-10/procesos.json` contiene **2094** registros, **794** con monto y **18441856682** CLP agregados; dispone de ranking monetario. Estas cifras están validadas en GitHub, no aún en Pages al momento de la captura.
- Las capturas 18:44–18:45 muestran que Pages aún entregaba la versión de analítica antigua, aunque el catálogo y los registros del período estaban actualizados. Causa técnica del desacople: el commit de derivados realizado con `GITHUB_TOKEN` no inicia un workflow `push` dependiente.
- Cambio publicado `6dff9d11`: el workflow `.github/workflows/preview-frontend-v2.yml` escucha `workflow_run` completado del workflow de derivados y ejecuta Pages solo si aquel termina correctamente, conservando activación por `push` y ejecución manual.
- Un despliegue en Pages fue iniciado para el commit de corrección (run `39859906294`), **pendiente confirmación de éxito y lectura pública del JSON**. No confundir generación satisfactoria con disponibilidad pública verificada.
- Pendiente para mañana: evaluar confiabilidad del cron GitHub de las 17:00 (UTC con validación de Santiago), instalación local del importador corregido y verificación integral de la cadena sin disparos manuales. No volver a ejecutar ETL para completar esta comprobación.
