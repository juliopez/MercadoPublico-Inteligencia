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
