# Investigación de divergencia catálogo / agregados de órdenes de compra

Fecha: 13/11/2026. Estado: **incidente de consistencia confirmado; causa raíz aún no demostrada; sin cambios productivos**.

## Evidencia directa en GitHub (rama principal)
Se comparó `frontend-v2/data/catalogo-publico.json` con `frontend-v2/data/analitica/YYYY-MM/ordenescompra.json`. Diferencia = agregado menos catálogo.

| Período | Catálogo OC | Agregado OC | Diferencia | Versión agregado |
|---|---:|---:|---:|---:|
| 2026-06 | 150551 | 150451 | -100 | 1 |
| 2026-07 | 151050 | 150980 | -70 | 1 |
| 2026-08 | 153438 | 153221 | -217 | 1 |
| 2026-09 | 148772 | 147966 | -806 | 1 |
| 2026-10 | 177972 | 167042 | -10930 | 3 |
| 2026-11 | 54984 | 67023 | +12039 | 3 |

**No corregir manualmente cifras ni elegir una fuente como verdad definitiva sin reconstruir su linaje.**

## Hallazgo en el generador actual
El archivo `scripts/generar_analitica_v2.py`:
1. Lee el catálogo vigente y obtiene `periodos[].partes[entidad]`.
2. Lee todos los fragmentos listados y suma sus filas.
3. Ejecuta `assert total == item["conteos"][entity]` **antes de escribir** `data/analitica/YYYY-MM/{entidad}.json`.
4. Escribe `version: 3` en el archivo generado.

Por tanto, **si el generador actual se ejecutó exitosamente con exactamente la misma versión del catálogo y los fragmentos que se publicaron**, sus totales deberían coincidir. Los archivos OC de junio–septiembre declaran versión 1, mientras el generador inspeccionado emite versión 3: es evidencia de un desfase de generación, no prueba concluyente de causa. Los archivos de octubre–noviembre son versión 3 pero difieren: también podrían haber cambiado catálogo, fragmentos, o publicación después de la generación, o haberse omitido una regeneración. Estas hipótesis requieren logs e historial de commits.

## Riesgo de integridad
El signo de noviembre es inverso a los otros cinco meses: no es seguro aplicar un ajuste uniforme ni asumir simple retraso de actualización. La cobertura y fecha del catálogo no certifican por sí solas que todos los derivados estén sincronizados.

## Contención ya implementada
`scripts/asistente_ia/backend/motor.mjs` compara `agregado.registros` con `catalogo.periodos[].conteos[entidad]`; ante discrepancia responde error 503 y **no entrega un monto ni conteo inconsistente**. Esta protección aplica al motor experimental; no se afirma que esté desplegado en Cloudflare.

## Siguientes comprobaciones, solo lectura
1. Ejecutar `node scripts/asistente_ia/backend/auditar_fuentes.mjs` en GitHub Actions de pruebas o entorno aislado; registrar resultados para las cuatro entidades y seis períodos.
2. Revisar historial de commits de catálogo, agregados OC y fragmentos para determinar el orden temporal de actualizaciones.
3. Revisar scripts y workflows que invocan `generar_analitica_v2.py`, y verificar si el publicador regenera los cuatro agregados después de modificar el catálogo.
4. Comparar conteos de fragmentos del catálogo con `conteos.ordenescompra` **sin modificar archivos**, para discriminar si el catálogo o el agregado quedó desfasado.
5. Solo tras localizar la causa, proponer una corrección separada con validación y aprobación expresa; no modificar ETL, cron, Sheets ni publicación como parte de esta investigación.

## Referencias
- [Generador analítico](../../scripts/generar_analitica_v2.py)
- [Auditoría de fuentes](../../scripts/asistente_ia/backend/auditar_fuentes.mjs)
- [Motor con bloqueo por inconsistencia](../../scripts/asistente_ia/backend/motor.mjs)
- [Inventario técnico](INVENTARIO_DATOS_ASISTENTE_IA_V2.md)

## Ampliación de trazabilidad: historial de commits (13/11/2026)
Se consultó el historial de GitHub:
- Commit `c4332251`: actualizó específicamente agregados de **procesos** de julio a noviembre, no los cuatro agregados de todas las entidades. Es evidencia de actualizaciones parciales por entidad.
- Commits `b112ef88` y `bb810745`: mensajes «actualizar índices y agregados 2026-11»; incluyen agregado de procesos e índices de búsqueda.
- Commit `c4b5f647`: incluye tanto `analitica/2026-11/ordenescompra.json` como `analitica/2026-11/procesos.json` e índices.
- Por lo tanto, **no es correcto afirmar que los agregados de OC nunca se regeneran**. Sí se observan actualizaciones con distinta selección de archivos; queda por verificar si todos los derivados son generados y publicados de forma atómica respecto al catálogo.

**Diagnóstico provisional:** la publicación puede contener versiones desalineadas entre catálogo y agregados. El historial es compatible con esa hipótesis, pero no demuestra aún la causa ni identifica el proceso responsable. Para atribuir responsabilidad se necesitan logs de ejecución, lista exacta de archivos en cada commit y comparación con el catálogo del mismo commit.

**Decisión de fase:** continuar fase 1 (motor seguro y pruebas) y fase 2 (consultas con fuentes consistentes), manteniendo bloqueadas las entidades/períodos cuyo agregado difiera. No corregir automáticamente datos publicados ni alterar el ETL.

## Ejecución real de auditoría — evidencia aportada 13/11/2026
Captura de GitHub Actions aportada por el usuario: workflow «Asistente IA - auditoría pública de fuentes», job `auditar`, URL `https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/43439795069/job/131934132010`, duración 34 segundos, estado **failed**. En el paso «Comparar catálogo y agregados públicos sin escribir datos», el reporte enumera discrepancias `Inconsistencia entre catálogo y agregado` para `ordenescompra` en los períodos 2026-06 a 2026-11. Terminó `Process completed with exit code 1`, que es el resultado esperado del auditor cuando encuentra fallas, **no una avería de la infraestructura de Actions**.

La captura muestra solo el tramo final del log: no permite afirmar cuántas verificaciones de otras entidades pasaron, ni el detalle completo de errores anteriores. Para completar la auditoría se requiere leer el log íntegro del job.

**Resultado de la fase 2:** bloqueo de datos incoherentes verificado en ejecución real; investigación de la causa raíz y reparación de la cadena de publicación pendientes de autorización y evidencia. No se alteraron archivos productivos.

## Log completo recuperado mediante GitHub API — 13/11/2026
Se recuperó íntegramente el log del job `131934132010` (run `43439795069`). Se verificaron **24 combinaciones** (6 meses × 4 entidades): **18 OK y 6 FALLA**. Desglose: procesos 6/6 OK; ofertas 6/6 OK; resultados 6/6 OK; órdenes de compra 0/6 OK. Los seis fallos corresponden exactamente a `ordenescompra` en 2026-06, 07, 08, 09, 10 y 11, con mensaje `Inconsistencia entre catálogo y agregado`. Fecha de publicación reportada: `2026-11-13T12:11:57.840734+00:00`. Commit comprobado en checkout: `b690cbd554eeea85feb9a033345f8ac78a497784`. Ejecución de auditoría entre 14:08:16 y 14:08:19 UTC. Resultado esperado: código 1 al detectar divergencias.

**Alcance:** se validó consistencia de conteos del catálogo frente a agregados y, en procesos, suma de modalidades; no se realizó reconciliación fila a fila de los fragmentos de origen ni se demostró que los montos sean correctos. La causa de la divergencia de OC sigue pendiente.

## Segunda auditoría real — fragmentos originales vs catálogo y agregados
Evidencia: captura de GitHub Actions `https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/43440956680/job/131938120327`, workflow «Asistente IA - trazabilidad fragmentos OC», job `auditar-fragmentos`, 13/11/2026. El script `auditar_fragmentos_oc.py` terminó con código 1 **porque detectó discrepancias**, no porque fallara su ejecución.

| Período | Fragmentos | Fragmentos faltantes | Filas fragmentos | Catálogo | Agregado |
|---|---:|---:|---:|---:|---:|
| 2026-06 | 151 | 0 | 150551 | 150551 | 150451 |
| 2026-07 | 152 | 0 | 151050 | 151050 | 150980 |
| 2026-08 | 154 | 0 | 153438 | 153438 | 153221 |
| 2026-09 | 149 | 0 | 148772 | 148772 | 147966 |
| 2026-10 | 178 | 0 | 177972 | 177972 | 167042 |
| 2026-11 | 55 | 0 | 54984 | 54984 | 67023 |

**Resultado:** `fragmentos_igual_catalogo: 6`, `fragmentos_igual_agregado: 0`. Se confirma que el **conteo** del catálogo refleja exactamente las filas de los fragmentos disponibles y que los seis agregados OC no reflejan esos mismos totales. No se infiere que todos los atributos o importes de cada fila sean correctos; esa validación no fue parte de esta auditoría.

**Diagnóstico:** los agregados OC publicados están desalineados respecto a los fragmentos y catálogo actuales. La causa operacional exacta (falta de regeneración, generación parcial o publicación no atómica) aún debe identificarse con logs/historial. No hay evidencia que justifique volver a consultar API ni reescribir MER.

**Siguiente decisión controlada:** identificar la invocación de `scripts/generar_analitica_v2.py` dentro del publicador y establecer la regeneración/verificación de OC tras actualizar los fragmentos; cualquier cambio productivo requiere aprobación expresa.

## Punto técnico identificado en el exportador V2 (inspección de código)
Se inspeccionó `scripts/exportar_frontend_v2.py`. Su función `main()` exporta una entidad y un período a staging, reemplaza `frontend-v2/data/partes/{entidad}/{periodo}` y actualiza `conteos`, `partes`, `huellas` y `fecha_publicacion` de `catalogo-publico.json`. **No invoca** `scripts/generar_analitica_v2.py` ni actualiza `frontend-v2/data/analitica/{periodo}/{entidad}.json` en ese mismo procedimiento.

**Implicación demostrada:** una ejecución del exportador sin un paso externo posterior de regeneración de agregados puede dejar el catálogo y los fragmentos actualizados mientras el agregado queda con la versión anterior. Este mecanismo es compatible con las seis discrepancias observadas; **no prueba por sí solo** que esa sea la secuencia concreta de las últimas publicaciones, pues falta inspeccionar el orquestador y sus logs.

**Próxima verificación:** identificar el script/workflow invocador y confirmar si, cuándo y con qué criterios ejecuta `generar_analitica_v2.py`. Diseñar corrección transaccional con verificación de integridad antes de publicar, pero no alterar el exportador ni el cron sin aprobación específica del cambio.

## Causa operacional identificada en workflow analítico (13/11/2026)
Se inspeccionaron directamente:
- `scripts/ubuntu_publicar_v2_post_etl.sh`: publica catálogo/fragmentos y anuncia que GitHub Actions regenerará derivados a las 17:00 Chile.
- `.github/workflows/generar-analitica-v2.yml`: **no tiene `schedule`**, `push` solo observa cambios en el propio YAML y `frontend-v2/js/analitica-visual.js`, y admite `workflow_dispatch`. Por tanto, **un push que solo modifica el catálogo y fragmentos no dispara este workflow**.
- El workflow recorre una lista fija de períodos `2026-06` a `2026-10`, excluyendo noviembre.
- El generador `scripts/generar_analitica_v2.py` emite `version: 3`, pero el paso de validación del workflow exige `a['version']==1`. Esta condición provocaría un error al regenerar con la versión actual.
- El workflow `.github/workflows/publicar-frontend-v2.yml` verifica que fragmentos y catálogo coincidan, pero no valida que los agregados analíticos correspondan a esos mismos datos.

**Conclusión técnica:** hay tres defectos verificables en el workflow analítico (disparador desconectado de datos, meses codificados y versión de validación incompatible). Son suficientes para explicar que la actualización de agregados no esté garantizada, aunque no permiten atribuir cada diferencia histórica a un único evento. La reparación debe evitar bucles de push y verificar la consistencia antes de publicar. **No se modificó ninguno de estos workflows productivos**; se requiere autorización explícita para el parche y su estrategia de recuperación de los seis meses.
