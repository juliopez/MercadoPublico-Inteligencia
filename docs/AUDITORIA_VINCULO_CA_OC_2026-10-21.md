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

## Verificación oficial puntual ejecutada (21-10-2026)

Se creó `scripts/verificar_oficial_ca_oc_v2.py` y el workflow `.github/workflows/verificar-oficial-ca-oc-v2.yml`, que utilizan `CHILECOMPRA_TICKET` solo como secreto del job, sin exponerlo. Se consultaron exclusivamente `839-4-COT26` en API v2 Compra Ágil y `839-10-AG26` en API v1 de órdenes de compra; no hubo escrituras en Sheets, ETL, históricos o índices.

**Resultado registrado:** [informe JSON](auditorias/VERIFICACION_OFICIAL_839-4-COT26_2026-10-21.json), [ejecución GitHub Actions #39695604848](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39695604848) **success**:

- API Compra Ágil HTTP **200**, pero no entregó en los campos públicos inspeccionados un código OC coincidente con `839-10-AG26`.
- API OC consultada por código devolvió HTTP **203**; no se obtuvo una confirmación de referencia cruzada.
- Dictamen automático: `pendiente_verificacion`, `coincidencia_oficial=false`, `verificacion_suficiente_para_vincular=false`.

**Decisión técnica:** la OC permanece como candidata no verificada y **no** se añade a las OC de código de proceso confirmado. El HTTP 203 no equivale a ausencia de OC ni a una respuesta probatoria. El siguiente paso requiere cotejar la ficha y documentación oficial de ambos códigos (por ejemplo, detalle y origen de la OC en el portal) o disponer de un endpoint que devuelva explícitamente su vinculación.

## Confirmación documental aportada por el usuario — 21-10-2026
El usuario consultó directamente MercadoPublico.cl y presentó tres capturas de pantallas oficiales: ficha de Compra Ágil `839-4-COT26` (FONASA), listado oficial de OC `839-10-AG26` (proveedor CAPACITACIONES ATRÉVETE SPA, aceptada) y, crucialmente, **detalle oficial de esa OC cuya descripción dice expresamente**: «Solicitud cotización ID 839-4-COT26 dirigida a CAPACITACIONES ATRÉVETE SPA». Esta referencia documental cruzada resuelve la ambigüedad de la búsqueda por similitud.

**Nuevo dictamen:** la asociación `839-4-COT26` → `839-10-AG26` está **confirmada documentalmente por la descripción oficial de la OC aportada en captura**, aunque el campo `codigo_proceso` de nuestros históricos está vacío y las consultas de API realizadas anteriormente no expusieron esa referencia. No confundir vínculo de origen con ejecución de pago.

**Acción implementada:** archivo público separado `frontend-v2/data/vinculos-oc-verificados.json` con códigos, fuente, alcance y evidencia. V2 muestra «OC vinculadas mediante evidencia documental» y excluye ese código de «OC candidatas por verificar». No se modificaron ZIP, JSON históricos, Google Sheets ni ETL. Este mecanismo es puntual; requiere procedimiento de revisión de evidencia oficial para confirmar futuros vínculos.
