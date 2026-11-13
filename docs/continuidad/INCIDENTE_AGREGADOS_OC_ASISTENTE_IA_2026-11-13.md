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
