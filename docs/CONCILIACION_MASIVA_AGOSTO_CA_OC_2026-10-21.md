# Conciliación masiva de órdenes de compra — agosto 2026

**Ejecución:** 21–22 de octubre de 2026. **Mandato del usuario:** procesar agosto completo en una sola ejecución, sin revisiones individuales.

## Procedimiento
Se procesaron todas las filas de agosto de los cuatro conjuntos públicos y se cotejaron las 153.221 órdenes de compra de agosto contra códigos de Procesos y selecciones/ofertas de **todos los períodos publicados junio–octubre 2026**. Se comprobó cada conteo de agosto contra el catálogo público V2.

Motor reproducible `scripts/conciliar_agosto_ca_oc_v2.py`. Workflow `.github/workflows/conciliar-agosto-ca-oc-v2.yml`. Salida auditable `frontend-v2/data/conciliacion/2026-08/resumen.json`; índices derivados separados en `directos/` y `candidatos/`, particionados por SHA-256 del código de proceso. **Sin modificar ZIP, CSV, JSON de origen, Google Sheets ni ETL**.

## Cobertura

| Registros públicos agosto | Cantidad |
|---|---:|
| Procesos | 83.937 |
| Ofertas | 432.111 |
| Resultados | 65.945 |
| Órdenes de compra | 153.221 |
| Códigos distintos de procesos accesibles en junio–octubre | 326.765 |

## Resultados

| Clasificación | Cantidad | Interpretación |
|---|---:|---|
| OC vinculadas por `codigo_proceso` exacto a un proceso publicado | **7.709** | Relación automática basada en referencia explícita del histórico |
| OC con referencia vacía | **92.522** | No pueden relacionarse por campo directo |
| OC candidatas distintas a uno o más procesos | **44.896** | Coinciden unidad compradora y proveedor seleccionado o de resultado; **no son vínculos confirmados** |
| Relaciones posibles generadas para esas OC | **197.910** | Una OC puede corresponder a varios procesos candidatos; no sumar como compras ni vinculaciones |
| OC candidatas ambiguas (más de un proceso potencial) | **20.914** | Requieren información oficial adicional |
| OC AG sin candidato por unidad y proveedor | **16.865** | No se encontró coincidencia bajo las reglas del piloto |
| Referencias no halladas entre los procesos publicados | **52.990** | Código OC de origen declarado, pero no existe proceso referenciado dentro del alcance disponible |

**Precisión:** la ejecución no recupera descripciones completas de la orden porque ese campo no está incluido en el esquema JSON V2 de OC. La segunda clasificación es de *candidatos*, no vínculos acreditados. El resultado no acredita pagos ni adjudicaciones contractuales.

## Caso de control
La OC `839-10-AG26` se recuperó como candidata única por unidad y proveedor para `839-4-COT26`, publicado en julio. **Existe, además, evidencia documental independiente** aportada por el usuario que acredita la referencia en la descripción oficial de esa OC; ese vínculo se conserva como verificado en `data/vinculos-oc-verificados.json` sin editar históricos. La conciliación estadística por sí sola no constituye esa evidencia.

## Efecto en la base
La base pública mejoró por incorporación de índices derivados y un reporte de conciliación auditable de agosto. **No se realizaron escrituras en la Google Sheet MER**, dado que la conciliación está basada en los fragmentos públicos y no existió autorización para modificar los campos históricos originales ni se cuenta con descripción oficial en todos los registros.

## Próximo trabajo técnico (no requerido para ejecutar este lote)
Para elevar candidatos a vínculos acreditados de forma general, incorporar descripción y referencia de origen de las OC desde históricos oficiales completos, extraer códigos COT y validar cruzadamente en lotes. No asignar 44.896 candidatas de forma automática. Extender a otros meses solo mediante una intervención separada.
