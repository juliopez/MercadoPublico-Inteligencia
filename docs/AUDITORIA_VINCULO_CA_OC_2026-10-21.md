# Auditoría de vínculos Compra Ágil → Órdenes de compra (V2)
**Caso investigado:** `839-4-COT26` · **21 de octubre de 2026**

## Alcance, fuente y reproducibilidad
Se consultaron los cinco períodos publicados (junio–octubre 2026) mediante `scripts/auditar_vinculo_ca_oc_historico_v2.py`. El programa validó la cantidad de filas de cada fragmento contra el catálogo y examinó **693.688 OC**, los procesos, las ofertas y los resultados disponibles. Archivo reproducible: [informe JSON](auditorias/AUDITORIA_VINCULO_839-4-COT26_2026-10-21.json). GitHub Actions: [#39693891909](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39693891909), `success`.

## Hallazgos confirmados
- `839-4-COT26` aparece en Procesos (julio), estado «Proveedor seleccionado», con 16 Ofertas y 1 Resultado.
- **0 OC enlazadas mediante igualdad exacta `codigo_proceso == 839-4-COT26`**, tras recorrer todos los fragmentos públicos.
- **418.961 de las 693.688 OC (60,4 %) tienen `codigo_proceso` vacío**: junio 90.948, julio 90.378, agosto 92.522, septiembre 89.909 y octubre 55.204. El vínculo exacto por ese campo tiene una limitación importante de cobertura.
- 280.521 OC tienen identificador terminado en `AG26`; el sufijo identifica un tipo de OC pero **no establece por sí solo el proceso de origen**.
- Coincide el proveedor seleccionado de las Ofertas y el informado como adjudicatario en Resultados: **CAPACITACIONES ATRÉVETE SPA**.
- Entre las **7 OC `839-*-AG26`** presentes en los históricos, se encontró **una candidata** con el mismo proveedor: `839-10-AG26`, de agosto de 2026, por **$1.650.000**, con `codigo_proceso` vacío.

## Dictamen
**Vinculación plausible, pero pendiente de verificación oficial.** El hecho de coincidir la unidad compradora (prefijo 839), el proveedor seleccionado y el período cercano convierte a `839-10-AG26` en candidata prioritaria. **No atribuir definitivamente esa OC a `839-4-COT26`** sin contrastar en la ficha oficial de Compra Ágil y la OC su referencia de origen, monto, fechas y organismo.

La ausencia de vínculo en V2 deriva de **insuficiencia del campo de referencia en la base pública**, no necesariamente de inexistencia de OC. Conservar la información histórica sin sobrescribir ni inventar referencias.

## Acción correctiva
1. **Completado:** auditoría reproducible de 693.688 OC y publicación de evidencia.
2. **Completado:** interfaz V2 aclara que «0 OC» significa ninguna coincidencia exacta en históricos, no ausencia de una OC oficial.
3. **Pendiente de verificación externa:** consultar ficha oficial del proceso `839-4-COT26` y OC candidata `839-10-AG26`; comparar identificadores cruzados y estados; obtener evidencia documental verificable.
4. **Pendiente de solución general:** diseñar índice de «OC candidatas sin código_proceso» separado de las OC **confirmadas**, priorizando referencias oficiales de origen; conciliar métricas de cobertura por mes y agregar avisos de vinculación incompleta.
5. **No autorizado / no efectuado:** rellenar `codigo_proceso` por similitud de proveedor, alterar datos originales, editar Sheets o regenerar todos los índices operativos.

Esta auditoría diagnostica el problema y deja una OC candidata; **no certifica que la candidata corresponda al proceso**.


## Segunda etapa — índices de OC candidatas y consulta pública

**Implementado:** `scripts/indexar_oc_candidatas_v2.py` construye, por mes, un índice independiente para OC con sufijo `AG`, proveedor informado y `codigo_proceso` vacío, agrupadas por **unidad compradora + nombre normalizado de proveedor**. No atribuye un `codigo_proceso` inexistente ni cambia el histórico. Archivo público: `frontend-v2/data/oc-candidatas/AAAA-MM/<hash>.json`, con metadatos por mes.

**Cobertura publicada y verificada:**
- Junio: 61.782 OC candidatas AG sin referencia, de 150.451 OC.
- Julio: 58.733 de 150.980.
- Agosto: 61.761 de 153.221.
- Septiembre: 60.792 de 147.966.
- Octubre: 37.493 de 91.070.

GitHub Actions de publicación [#39694526927](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39694526927): `success`. Verificación de la sintaxis e integración de V2: [#39694607358](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39694607358): `success`.

**Interfaz:** la pestaña Órdenes de compra mantiene las **coincidencias exactas confirmadas por campo de código**; ahora dispone de una lista independiente de **«OC candidatas por verificar»** cuando el proceso tiene proveedor seleccionado o adjudicatario informado. Consulta solo una partición indexada por mes y proveedor, sin descargar todas las OC. La selección de proveedor procede de campos de Resultados u Ofertas seleccionadas. El código candidato es navegable como OC; **no se presenta como asociación contractual confirmada**.

**Caso principal:** `839-4-COT26` tenía candidato `839-10-AG26` por unidad 839 y proveedor CAPACITACIONES ATRÉVETE SPA, por $1.650.000. Se espera que aparezca como *candidato* y no en «OC vinculadas» hasta obtener referencia oficial. La consulta web abierta no permitió obtener una ficha oficial verificable para esos dos códigos; **la validación externa sigue pendiente**. La mejora no resuelve por sí sola la identificación legal sin RUT ni la conciliación de referencias oficiales.

**Pendiente:** prueba visual del usuario y cotejo en fuente oficial antes de marcar cualquier OC como vinculada; valorar fechas, monto ofertado versus monto OC, identidad de unidad y posibles homónimos. Auditoría integral V2 permanece pendiente.
