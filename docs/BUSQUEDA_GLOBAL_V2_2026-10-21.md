# Búsqueda global V2 — avance de diseño e implementación (21-10-2026)

## Objetivo
Recuperar de V1 la búsqueda de procesos, organismos y proveedores en todo el período sin sustituir el motor de carga fragmentada de V2.

## Consulta previa
README principal, índice, decisiones, línea base V2, documento de filtros locales y código de app.js, index.html y exportar_frontend_v2.py.

## Trabajo realizado
Se incorporó `scripts/indexar_busqueda_frontend_v2.py`, generador inicial que opera únicamente sobre los JSON públicos `frontend-v2/data/partes`, valida recuentos del catálogo y prepara un índice por período, entidad y prefijo de tres caracteres de palabra. Incluye campos de consulta públicos: códigos, nombres de procesos, organismos y proveedores. No lee ni escribe Sheets ni afecta los ETL.

## Estado y limitaciones
**En desarrollo, no operativo.** El generador todavía no se ha ejecutado y validado sobre millones de registros; no hay índices publicados ni búsqueda global habilitada en frontend. Antes de integrarlo es imprescindible medir tamaño y memoria del proceso de indexación, comprobar nombres y coincidencias, controlar términos frecuentes y publicar de manera transaccional sin saturar GitHub Pages. El índice por prefijos no equivale a búsquedas arbitrarias de subcadenas; búsquedas de menos de tres caracteres quedan fuera de alcance inicial. No afirmar cobertura global en la interfaz existente.

## Archivos y cambios
- Nuevo: `scripts/indexar_busqueda_frontend_v2.py`.
- Sin cambios: app.js, HTML, CSS, índices relacionados, manifiesto, fragmentos de datos, frontend V1 y datos privados.

## Validación y siguiente hito
Se inspeccionó código/documentación y se corrigió la serialización de saltos de línea. No se ejecutaron pruebas automatizadas ni navegador. Antes de activar funcionalidad, validar el generador con dataset reducido y posteriormente con cobertura real; generar índice y comprobar búsqueda selectiva end-to-end, sin regresión de rendimiento de V2.


## Continuación — validación preventiva (21-10-2026)
- Se volvió a leer README, índice, decisiones y este documento antes de intervenir.
- Se detectó y corrigió una expresión regular que rechazaba rutas de fragmentos JSON válidos: commit `96f865db`.
- Se incorporó `tests/test_indexar_busqueda_frontend_v2.py`, con casos para índice de dos procesos, normalización con tildes, prefijos y discordancia de conteos: commit `e9a4692b`.
- **Pruebas aún no ejecutadas contra el código del repositorio:** la conexión de red del entorno local de verificación no permitió obtener el archivo remoto. Los nuevos casos de prueba quedan disponibles para ejecución en CI o en entorno de desarrollo.
- No se generaron índices masivos ni se modificó el JavaScript de carga y búsqueda actual. La interfaz continúa utilizando búsqueda local por bloque.
- Riesgos pendientes: volumen y tamaño de prefijos frecuentes, uso de memoria durante indexación, duplicación de texto por clave y latencia. No activar búsqueda global antes de medirlos.


## Continuación — incorporación de CI
Se revisaron nuevamente README, índice, decisiones y documentación de búsqueda antes de intervenir. Se añadió `.github/workflows/validar-busqueda-v2.yml` (commit `d0ba59f0`) para ejecutar comprobación de sintaxis y las dos pruebas unitarias del generador directamente sobre el checkout real en GitHub Actions. El workflow se inicia por cambios en sus propios archivos o manualmente.

**Verificación pendiente:** la herramienta de consulta no permitió obtener la lista de ejecuciones del workflow. No se afirma que las pruebas hayan pasado ni se publica un índice sin esa evidencia. Tampoco se ha medido tamaño con los históricos. Se mantienen intactos frontend V1, JavaScript de V2, carga fragmentada, Sheets y ETL.


## Comprobación adicional — 21-10-2026
- Se consultó documentación vigente antes de continuar.
- Se comprobaron los estados asociados al commit del workflow `d0ba59f0`; las consultas de estado devolvieron `statuses: []` y `workflow_runs: []`. **No hay evidencia obtenida de una ejecución CI satisfactoria.**
- La red del contenedor no logró resolver GitHub. Se ejecutó **una reproducción local aislada de la lógica principal** con dos registros sintéticos: normalización de tildes, creación de prefijos, acceso a los registros por prefijo, validación de rutas y detección de discordancia de recuentos; el ensayo finalizó correctamente. Esto **no sustituye la ejecución del test original del repositorio**.
- No se ejecutó una medición real de tamaño o consumo de memoria con el conjunto histórico completo; el navegador V2 sigue con búsqueda por bloque. No se habilitó nueva funcionalidad ni se modificó el sistema de carga.
- Antes de desplegar índices globales, confirmar éxito de CI y establecer límites para prefijos frecuentes que podrían generar archivos muy grandes.


## Revisión de seguimiento tras aprobación — 21-10-2026
- Se releyeron README, índice, decisiones, documento específico y el código del generador y pruebas.
- Se intentó obtener el checkout de GitHub en el entorno de ejecución; falló por resolución DNS de `github.com`. La consulta web a la página del workflow también resultó inaccesible. No existe evidencia obtenida de una ejecución de CI ni de mediciones sobre los archivos reales.
- Se ejecutó `python /mnt/data/mpv2_check/check.py` en el entorno aislado de trabajo; resultado `PASS pruebas aisladas: prefijos, acentos, conteos y rutas`. Este archivo reproduce una parte de la lógica y **no sustituye el test del repositorio**, por lo que no se eleva su estado a prueba integral.
- Hallazgo sobre dimensionamiento: el algoritmo mantiene `buckets` con textos repetidos para varios prefijos de cada fila. Con cientos de miles de registros podría crecer mucho en memoria y producir archivos de prefijos frecuentes poco eficientes. El índice requiere rediseño o un ensayo acotado instrumentado antes de desplegarlo; **no está aprobado su uso masivo**.
- No se ha editado código ni desplegado datos en esta revisión: prioridad preservar la carga por fragmentos validada.


## Optimización del formato — continuación 21-10-2026
Se consultaron README, índice, decisiones, documento específico y código del indexador y sus pruebas antes de intervenir. El índice por prefijos fue ajustado para almacenar únicamente pares `[indice_fragmento,indice_fila]` en lugar de tripletas `[indice_fragmento,indice_fila,texto_normalizado]`, manteniendo la selección por prefijos de palabras. El metadato pasa a `version=2` y declara `formato=referencias_fragmento_fila`. Se actualizaron los casos unitarios para verificar tanto las coincidencias como que ninguna fila del índice incluya texto.

**Commits:** `0690f729` (generador) y `49a36462` (pruebas).

**Estado:** código implementado y contrastado estáticamente; **no se han ejecutado las pruebas contra el checkout ni medido los tamaños reales**. Los arrays de referencias continúan en memoria durante la generación y los prefijos frecuentes pueden originar archivos grandes, por lo que el consumo no se considera validado. Tampoco se publicaron índices, se cambió el frontend o se alteraron Sheets, ETL o V1. Se requiere CI exitosa y dimensionamiento instrumental antes de conectar búsqueda global.
