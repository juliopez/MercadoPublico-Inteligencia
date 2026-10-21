# Cierre supervisado MER v2 — Octubre 2026

**Fecha:** 10 de noviembre de 2026. **Objetivo:** solo ejecutar y verificar; **no desarrollar código**.

## Decisiones cerradas

- **Unidad de carga:** mes calendario. El ZIP oficial de octubre corresponde a octubre, no se extrapolan registros a otros períodos.
- **Autoridad de datos:** la última descarga oficial de Mercado Público del mes prevalece sobre valores divergentes de la hoja operativa con la misma PK; se reemplaza la fila por la oficial completa. Las PK presentes solo en el operativo se conservan para no perder información sin respaldo y quedan reflejadas en los informes; no se hacen eliminaciones automáticas.
- **Destino:** la hoja existente `MER_2026_10_OPERATIVO`, ID `1v12ztJfxvltzv1rJQBsxxmyMwmnuc2DUx87SeRCSnz4`. Al cerrar se traslada **el mismo archivo y el mismo ID** a `01_Historicos_MER`, con nombre `MER_2026_10`.
- **Alcance:** seis pestañas: `Procesos`, `Ofertas`, `Resultados`, `OrdenesCompra`, `Proveedores`, `VinculosCOT_OC`.
- **Fuente:** tres ZIP oficiales: licitaciones, Compra Ágil (COT) y órdenes de compra del mes. Si falta uno, el cierre no continúa.
- **Credenciales:** el JSON ya existente en Ubuntu (`$HOME/.config/mercadopublico/servicio-google.json`), sin volver a descargarlo. Para actualización de catálogo se requiere GitHub CLI autenticado o token local seguro.
- **Seguridad:** respaldo ZIP verificable antes de escribir; candado compartido con el ETL diario; control de modificaciones entre lectura y escritura; relectura de todas las tablas tras aplicar; aprobación documentada antes del traslado.
- **No instalar cron mensual** hasta confirmar esta primera ejecución.

## Antes del 10 de noviembre — verificaciones no destructivas

En el repo local Ubuntu:
```bash
git pull --ff-only
bash scripts/ubuntu_cierre_supervisado.sh verificar-acceso
gh auth status
```
El verificador usa el JSON local e informa permisos sobre las carpetas y la hoja de octubre. **Si la cuenta de servicio no puede trasladar entre carpetas del propietario, detener el traslado**: el JSON no convierte a la cuenta de servicio en propietaria. En tal caso se puede realizar el movimiento con la cuenta propietaria desde Drive y luego actualizar/confirmar el catálogo GitHub; esto es una tarea operativa, no requiere desarrollar más scripts. No exponer tokens o JSON en los logs.

## 10 de noviembre — ejecución

```bash
git pull --ff-only
bash scripts/ubuntu_cierre_supervisado.sh diagnosticar --periodo 2026-10
```
Leer `~/.local/share/mercadopublico/cierres/2026-10/resumen_diagnostico_cierre.json` y `precedencia_oficial_mensual.json`. El estado requerido es `DIAGNOSTICO_OFICIAL_MENSUAL_LISTO_PENDIENTE_CARGA`. Los conflictos entre valores divergentes se anotan como información y se resuelven por precedencia mensual; los problemas de integridad bloqueantes, no.

```bash
bash scripts/ubuntu_cierre_supervisado.sh cargar --periodo 2026-10
```
Confirmar `constancia_carga_real.json`, respaldo ZIP y verificación final. Si falla una tabla, **no trasladar**; la carga se puede reanudar bajo supervisión.

Solo después de verificación, documentar la aprobación del archivo:
```bash
mkdir -p "$HOME/.local/share/mercadopublico/cierres/2026-10"
cat > "$HOME/.local/share/mercadopublico/cierres/2026-10/APROBACION_CIERRE.json" <<'JSON'
{"periodo":"2026-10","spreadsheet_id":"1v12ztJfxvltzv1rJQBsxxmyMwmnuc2DUx87SeRCSnz4","aprobar_traslado":true}
JSON
bash scripts/ubuntu_cierre_supervisado.sh trasladar --periodo 2026-10
```
**Esta aprobación NO se crea antes de comprobar la carga.**

## Resultado verificable

La misma hoja pasa de `02_Operativo_MER` a `01_Historicos_MER`, conserva ID, se actualiza `config/catalogo_sheets.json` en GitHub, se genera `constancia_traslado.json` y se inspeccionan los logs fechados.

Si Drive confirma movimiento y falla GitHub, repetir **solo** `trasladar`; no repetir el movimiento ni cargar de nuevo. Si no hay capacidad de traslado con la cuenta de servicio, usar la cuenta propietaria para mover el mismo archivo y ejecutar después `trasladar`, que reconoce Drive ya movido.

## Automatización posterior

Solamente después de un cierre de octubre satisfactorio, programar cron mensual para iniciar el 10 de diciembre de 2026. El cron diario actual permanece independiente.

## Evidencia y límites

GitHub Actions valida código Python, sintaxis Bash y pruebas unitarias, pero no puede verificar el JSON almacenado en Ubuntu ni probar remotamente permisos de Drive con esa identidad. Una comprobación de permisos exitosa es un requisito previo; **no confundir validación del código con cierre de producción ejecutado**.
