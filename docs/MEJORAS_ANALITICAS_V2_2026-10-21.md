# Mejoras analíticas V2 — prioridades 1 a 4

**Fecha:** 21-10-2026. Se ejecutan juntas por aprobación del usuario; la **prioridad 5 (auditoría integral) queda expresamente separada y pendiente**.

## Consulta previa
Se revisaron README, índice documental, decisiones técnicas, HTML y JavaScript vigentes del frontend V2 y el catálogo público, antes de modificar.

## 1. Filtros globales
Se añadieron controles por Estado y Modalidad/Tipo sobre la **búsqueda global indexada**. Los filtros se evalúan sobre los registros realmente recuperados de cada candidato del mes. Cada entidad usa sus campos: Procesos (estado, modalidad); Ofertas (seleccionado); Resultados (validado); Órdenes de compra (estado, tipo_oc). **Requiere al menos una palabra clave de tres caracteres**; todavía no hay índices de facetas independientes para buscar todo el mes solamente por estado. Las búsquedas siguen paginadas en 10 y leyendo bloques selectivamente.

## 2. Indicadores analíticos
Panel de evolución mensual por entidad calculado **directamente de conteos del catálogo** (sin descargar datos históricos). La búsqueda global añade cantidad de coincidencias verificadas, cantidad con monto y suma descriptiva de montos informados; hasta completar la exploración indica que es cifra parcial. No equivale a compras o contratos únicos y no se infieren adjudicaciones.

## 3. Exportación global CSV
Se puede exportar la **consulta global completa tras verificar todos sus candidatos**, con filtros aplicados, siempre que no exceda 20.000 coincidencias exactas. Si el límite se excede se rechaza la descarga y se pide refinar la consulta; **nunca exportar silenciosamente un subconjunto como si fuera completo**. Se mantiene la exportación local por bloque, distinta y etiquetada. El CSV usa separador ;, UTF-8 BOM y neutralización básica de campos de fórmula.

## 4. Vínculos de perfiles
La ficha contextual permite lanzar una consulta global del actor: organismos en Procesos; proveedores en Ofertas, Resultados informados y Órdenes de compra. Los vínculos reutilizan el índice de búsqueda y el lector actual, sin descargar masivamente el mes. Como la unión es por nombre normalizado, no identifica empresas por RUT ni acredita relación contractual. La tabla de Procesos no permite aún conectar de forma inequívoca organismos con OC porque esa tabla no publica un identificador de organismo comprador.

## Archivos
- `frontend-v2/index.html`
- `frontend-v2/js/busqueda-global.js`
- `frontend-v2/js/app.js`
- `frontend-v2/css/styles.css`
- `.github/workflows/validar-paquete-analitico-v2.yml`

## Evidencia y pendientes
Workflow: https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39668529243 . Consultar su estado antes de afirmar resultado. La prueba automatizada revisa sintaxis, lógica de filtrado, elementos y enlaces; no sustituye pruebas completas de usuario en navegador. La auditoría integral de V2 se reserva como quinta tarea autónoma, sin iniciarse en esta entrega. Sin cambios a V1, ETL, Sheets ni datos históricos.


## Validación de la intervención conjunta
La primera ejecución [#39668529243](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39668529243) detectó un error de sintaxis en el nuevo módulo global. Tras corregir el mensaje de indicadores y eliminar un bloque duplicado, la ejecución [#39668903402](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39668903402) terminó **completed/success**. Se verificaron sintaxis de los tres módulos JavaScript y pruebas de coincidencias positivas/negativas para estado y modalidad, además de la presencia de controles y lógica principal de CSV, evolución y enlaces de perfiles.

**Limitaciones que permanecen:** filtros globales requieren término de búsqueda (no hay navegación por faceta independiente); suma y cantidad son acumulados de coincidencias verificadas hasta esa página, a menos que la búsqueda se recorra completamente; exportación global rechaza más de 20.000 filas en lugar de producir un fichero incompleto; enlaces de perfiles por nombre normalizado, no por RUT; y no se ha ejecutado prueba visual final para estas cuatro funciones. La **auditoría integral (prioridad 5) queda explícitamente pendiente para una intervención separada**.


## Autocompletado de filtros globales — 21-10-2026
Por aprobación del usuario se añadieron sugerencias a los tres controles globales (Palabras clave, Estado, Modalidad/Tipo) desde `frontend-v2/js/sugerencias-global.js` y `datalist` en `frontend-v2/index.html`. El origen son exclusivamente JSON públicos precomputados, no las hojas privadas ni una descarga masiva desde el navegador. El generador `scripts/generar_sugerencias_busqueda_v2.py` calcula frecuencias por token de los campos indexados, limita cada archivo de prefijo a 120 palabras frecuentes y publica listas de valores de estado y modalidad por entidad. El cliente consulta el grupo al escribir dos letras o muestra sugerencias de faceta al enfocar el campo; ofrece hasta 30 opciones, mantiene escritura libre y presenta fallos de acceso sin bloquear la consulta. Las sugerencias son orientativas, no lista exhaustiva de vocabulario, y para Palabras clave corresponden a **tokens**, no a títulos o nombres completos.

Workflow de publicación: [#39670057198](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39670057198). Al registrar este texto estaba `in_progress`; comprobar éxito y metadatos antes de afirmar cobertura. **Prioridad 5: auditoría integral permanece sin ejecutar.**
