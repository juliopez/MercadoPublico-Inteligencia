# Auditoría diferencial COT–OC — junio a septiembre 2026

**Fecha de cierre documental:** 21 de octubre de 2026. **Origen de evidencia:** `resumen.json` generado en Ubuntu por el auditor diferencial, compartido por el usuario. Ejecución real, modo `SOLO_LECTURA_SIN_ESCRITURA_MER`. No es una ejecución de GitHub Actions ni una nueva carga de datos.

## Resultados contra archivos ZIP COT originales y MER histórico

| Período | Pares explícitos ZIP COT | Pares MER únicos | Coinciden | Faltantes en MER | Exclusivos MER |
|---|---:|---:|---:|---:|---:|
| 2026-06 | 65.867 | 65.867 | 65.867 | 0 | 0 |
| 2026-07 | 56.149 | 56.149 | 56.149 | 0 | 0 |
| 2026-08 | 68.592 | 68.593 | 68.592 | 0 | 1 |
| 2026-09 | 50.041 | 50.041 | 50.041 | 0 | 0 |
| **Total** | **240.649** | **240.650** | **240.649** | **0** | **1** |

Ningún mes registra pares duplicados ni anómalos en MER según el informe. El par exclusivo MER de agosto es consistente en cantidad con el vínculo documental agregado por separado `839-4-COT26` → `839-10-AG26`; el `resumen.json` **no identifica por sí mismo dicho par**, por lo que su identidad proviene de la constancia anterior [Conciliación de agosto](CONCILIACION_MASIVA_AGOSTO_CA_OC_2026-10-21.md).

## Interpretación y decisión de continuidad

**Cerrado:** conciliación de todos los pares explícitos `CodigoCotizacion` / `CodigoOC` presentes en los ZIP COT de junio–septiembre. No volver a cargar estos pares ni ejecutar nuevamente la auditoría sin cambio de fuentes o reglas.

**Pendiente distinto:** órdenes de compra cuyo vínculo con COT no aparece en el campo estructurado del ZIP COT, ni en `codigo_proceso` de la tabla OC. Requieren evidencia de origen adicional (por ejemplo, descripción oficial de la OC). Las coincidencias de unidad/proveedor son candidatas no confirmadas.

**Orden eficiente de trabajo:**
1. Inspeccionar sin modificaciones los campos de los ZIP oficiales OC **ya conservados**, buscando descripción o referencia libre a códigos `-COT26`. El importador MER actual selecciona un subconjunto y omite campos libres; no inferir ausencia en el ZIP a partir de la ausencia en V2.
2. Si existen, extraer únicamente pares explícitos y cotejar por lote con los 240.650 vínculos almacenados, dejando evidencia de archivo, columna y texto de origen. No crear asociaciones por similitud.
3. Solo si los ZIP no contienen el dato, comprobar de forma acotada si una API o ficha oficial proporciona la descripción, sin hacer llamadas masivas antes de acreditar cobertura.
4. Publicar informe diferencial y, tras respaldo y autorización para escritura, incorporar únicamente nuevos pares comprobados, con PK determinística y verificación posterior.

## Control de cambios

Esta documentación no altera V1, V2, hojas MER, ZIP históricos, workflows, ETL ni cron diario. Estados de evidencia: **código de importación implementado**; **auditoría Ubuntu ejecutada y resultados revisados**; **ninguna nueva actualización de MER** por esta auditoría; enriquecimiento de OC **pendiente**.
