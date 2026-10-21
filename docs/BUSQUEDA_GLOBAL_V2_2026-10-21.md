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


## Instrumentación del rendimiento — continuación aprobada
Tras releer README, índice documental, decisiones y este documento, se intentó ejecutar las pruebas originales mediante descarga HTTPS de GitHub: bloqueo por DNS (`raw.githubusercontent.com` no resoluble). No se afirman resultados de esas pruebas ni del workflow.

Se añadió `tests/benchmark_busqueda_frontend_v2.py` (commit `08e8d00d`) para generar **20.000 registros sintéticos en 20 fragmentos**, ejecutar el índice compacto y reportar tiempo, memoria máxima del proceso, bytes totales, número de archivos y tamaño del prefijo más grande. El workflow `.github/workflows/validar-busqueda-v2.yml` fue ampliado para ejecutar el benchmark después de las pruebas unitarias (commit `28c5971c`).

**Estado de evidencia:** benchmark automatizado incorporado, **sin resultado de ejecución confirmado todavía**. Esta prueba sintética no sustituye medir las entidades históricas ni demuestra escalabilidad a millones de registros. No se generaron índices públicos ni se modificaron V1, JS de V2, datos, Sheets o ETL. Se mantiene la búsqueda global desactivada hasta evaluar cifras medidas.


## Resultado de GitHub Actions confirmado — ejecución #39658799509
**Fuente comprobada:** ejecución [#39658799509](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39658799509), trabajo `tests` #119426064019, conclusión `success`, registrada el 21-10-2026 UTC. Se consultaron los registros originales del trabajo.

- Sintaxis Python: éxito.
- Pruebas unitarias: **2 ejecutadas, 2 correctas** (`Ran 2 tests in 0.003s`).
- Benchmark **sintético**, no histórico: **20.000 registros**, **0,405 segundos** de construcción, **910 archivos JSON**, **1.846.369 bytes** de índice total, **167.802 bytes** el archivo más grande y **38.156 KB** de memoria máxima reportada por el proceso.
- Mensaje del generador: `BUSQUEDA_INDICE_OK 2026-06 procesos 20000 909` (909 particiones de prefijos + meta.json = 910 archivos).

**Interpretación:** éxito de la prueba sintética e integración de CI, sin extrapolar esos tiempos, tamaños o memoria a millones de registros. La fragmentación en 909 archivos y las palabras de alta frecuencia requieren evaluación con históricos antes de generar/publicar índices y habilitar la búsqueda global. Ningún dato de Google Sheets, ETL ni frontend V1/V2 se modificó para esta verificación.


## Ensayo con histórico público real — 21-10-2026
Se revisaron README, índice, decisiones y el documento específico antes de intervenir. Se añadió `tests/benchmark_busqueda_historica_v2.py` (commit `4685afc6`): utiliza **los primeros 50 fragmentos de Ofertas de junio 2026** ya publicados, confecciona un manifiesto temporal con el recuento exacto de esa muestra y construye el índice en `TemporaryDirectory`, enlazando los fragmentos públicos originales solo para lectura. Reporta registros, tiempo, memoria máxima, tamaño total y tamaño mayor de archivo. No accede a Google Sheets.

Se actualizó `.github/workflows/validar-busqueda-v2.yml` (commit `b5cf0cb5`) con el benchmark de históricos reales y límite de 15 minutos para el trabajo. GitHub Actions inició automáticamente la [ejecución #39659422313](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39659422313). **Última consulta durante esta edición:** `in_progress`, checkout en ejecución; no atribuir éxito ni cifras hasta consultar su conclusión y logs. Se preservan V1, V2, datos, ETL y Sheets.


## Resultado confirmado de benchmark histórico — ejecución #39659422313
GitHub Actions [#39659422313](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39659422313) terminó con `conclusion=success`; job `119428225566`. Verificados los logs originales el 21-10-2026.

**Ofertas reales, junio 2026, primeros 50 fragmentos:** 50.000 registros; 1,133 segundos; memoria máxima **46.932 KB** (métrica de proceso); **3.116 archivos** (3.115 prefijos y un `meta.json`); **2.656.877 bytes** de archivos generados; archivo mayor **434.502 bytes**. Registro: `BUSQUEDA_INDICE_OK 2026-06 ofertas 50000 3115`.

Las **2 pruebas unitarias también aprobaron** en esta ejecución. Benchmark sintético ejecutado en el mismo job: 20.000 filas, 0,657 s, 38.100 KB, 1.846.369 bytes.

**Alcance:** resultados reales de una muestra de 50 fragmentos, no del período completo de 407.923 Ofertas ni de millones de registros. Los 3.116 archivos ponen en evidencia un costo operativo importante si se publican los índices como archivos individuales; se debe evaluar empaquetado/rangos y respuestas de términos frecuentes antes de integrarlos al navegador. No se publicaron los archivos de índice ni se alteraron los sistemas actuales.


## Consolidación física de prefijos — 21-10-2026
- Revisados README, índice, decisiones, documento de búsqueda, generador, pruebas y workflow antes de intervenir.
- El índice pasó de un archivo por prefijo de tres caracteres a un archivo por sus dos primeros caracteres, con un diccionario `prefijo -> [[fragmento,fila], ...]`. La búsqueda futura leerá el grupo correspondiente y recuperará solamente el prefijo buscado. No hay cambios en el motor de carga de V2 ni publicación de índices.
- Generador: versión de contrato de índice **3**, metadatos `grupos` y `particiones`; commit `041a71be`. Prueba unitaria ajustada: commit `8a9c00a0`.
- GitHub Actions lanzó automáticamente la ejecución [#39659762031](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39659762031). **En progreso en la última consulta de esta anotación**; obtener conclusión y métricas antes de hablar de mejora cuantitativa.
- Restricción: agrupar reduce el número de archivos pero puede aumentar el tamaño máximo de una descarga; medir especialmente el mayor grupo en la muestra real de Ofertas antes de integrar el navegador.


## Resultado verificado del índice agrupado — ejecución #39659762031
Se consultaron los logs del trabajo `119429401700` en la ejecución [#39659762031](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39659762031): `success`, dos pruebas unitarias correctas.

**Muestra histórica real:** Ofertas junio 2026, 50 fragmentos, 50.000 registros. Nuevo formato v3: 3.115 prefijos consolidados en 519 grupos (520 archivos incluyendo `meta.json`); 0,951 segundos; 2.676.631 bytes totales; mayor archivo 553.545 bytes; memoria máxima 46.960 KB.

**Comparación misma muestra formato v2 anterior:** 3.116 archivos, 1,133 segundos, 2.656.877 bytes, archivo mayor 434.502 bytes, 46.932 KB de memoria. Reducción de archivos de aproximadamente **83,3 %** a cambio de leve aumento de bytes, tamaño máximo y memoria. Son mediciones de runners CI diferentes, no benchmarks controlados repetidos, y no se extrapolan a toda la historia.

Benchmark sintético del nuevo formato: 20.000 registros; 0,622 segundos; 100 archivos; 1.852.046 bytes; máximo 176.684 bytes; 38.180 KB.

**Decisión operativa:** índice agrupado v3 validado en muestra real, sin publicación masiva ni activación del buscador. Siguiente hito: probar tamaño del grupo más frecuente y cobertura de la entidad completa, y después integrar búsqueda selectiva al frontend sin sustituir `loadChunk()`. La V1 y los datos/ETL/Sheets se mantuvieron intactos.


## Cierre del benchmark mensual completo — 21-10-2026
La ejecución [GitHub Actions #39660049638](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39660049638), job `119430375028`, completó con `success`, según consulta directa al job y a sus logs. Cobertura real total de **Ofertas junio 2026**: **408 fragmentos, 407.923 registros**, concordantes con el catálogo público. Índice agrupado: 4.046 prefijos repartidos en **604 grupos (605 archivos incluyendo metadatos)**. Métricas: **7,734 segundos** de generación; **23.975.509 bytes** totales; **4.997.582 bytes** del mayor archivo; **254.392 KB** de memoria máxima del proceso en runner Linux. Dos pruebas unitarias correctas.

La medición se realizó en directorio temporal sin publicar índices o modificar los fragmentos originales, Sheets ni V1/V2. **Se considera cerrada la prueba de escalabilidad de generación para un mes completo de Ofertas**. La validación no mide aún latencia de búsqueda por navegador, y el archivo más pesado (~5 MB) requiere descarga selectiva, límites y manejo de errores.

**Siguiente fase:** integración funcional de la búsqueda indexada con manejo de consulta, límites de resultados, paginación y accesos a fragmentos. No generar más experimentos de tamaño por incrementos; pasar a entrega visible tras pruebas funcionales.
