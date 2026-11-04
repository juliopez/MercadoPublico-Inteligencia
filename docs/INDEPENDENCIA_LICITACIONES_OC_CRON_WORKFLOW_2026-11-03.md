# Independencia de licitaciones y órdenes de compra — cron y publicación V2

**Fecha:** 03-11-2026. **Responsable del cambio funcional aprobado:** operación del Observatorio MER. **Alcance:** proceso 1, cron Ubuntu de las 16:00, y su workflow de derivados de GitHub Actions. Este documento distingue la **separación efectivamente validada** de las **fallas no aisladas todavía**. No atribuir disponibilidad total a una protección parcial.

## 1. Principio operativo

**Una fuente oficial sin registros no debe impedir procesar la otra cuando esta contenga datos válidos**, ni debe interpretarse un CSV vacío como instrucción de borrar datos históricos o vigentes en Google Sheets. La publicación de una entidad solo es admisible con origen y lectura posterior verificados. Licitaciones y órdenes de compra son entidades independientes en la carga; los vínculos documentales entre ellas pueden seguir pendientes.

**No se agrega un segundo cron**: se mantiene la invocación Ubuntu de lunes a viernes a las 16:00, `scripts/ubuntu_cron_integrado.sh --cron`. No se altera la API nocturna de Compra Ágil, los temporizadores de rotación mensual ni la consolidación histórica.

## 2. Cadena real de ejecución

1. `scripts/ubuntu_cron_integrado.sh`: comprueba horario/credenciales, adquiere bloqueo y llama al ETL existente.
2. `scripts/ubuntu_etl_dos_fuentes.sh`: bloqueo compartido de escritura, bitácora y ejecución de `scripts/etl_zip_dos_fuentes.py`.
3. `scripts/etl_zip_dos_fuentes.py`: **descarga ambos ZIP**, comprueba ZIP/CRC, procesa en staging SQLite y decide **por entidad** qué hojas de MER actualizar:
   - `Procesos` solo si existen licitaciones procesables.
   - `OrdenesCompra` solo si existen OC procesables.
   - `Proveedores` cuando existen proveedores procesables.
   - `Ofertas`, `Resultados` y `VinculosCOT_OC` no se rellenan con ceros por ausencia de una fuente; se preservan.
   - Realiza **respaldo completo de las seis hojas** antes de escribir, upsert por PK, y relectura de PK y contenido tras cada hoja escrita.
4. `scripts/registrar_sincronizacion.py`: valida que el informe corresponda al inicio y a la ejecución actual. Declara `EXITOSA` con `cobertura=PARCIAL_VERIFICADA` cuando solo una fuente se incorporó correctamente; no equivale a cobertura total.
5. El orquestador ejecuta conciliación documental y `scripts/ubuntu_publicar_v2_post_etl.sh` después de verificar la escritura. Exporta los fragmentos y el catálogo y los publica en GitHub.
6. El workflow `.github/workflows/publicacion-v2-post-etl.yml` comprueba exportación reciente, construye búsqueda, perfiles, analítica e índices de relaciones y **solo publica derivados si se completan todas sus validaciones**.

### Diagrama de resultados

| Licitaciones ZIP | OC ZIP | Comportamiento de ETL actual | Protección |
|---|---|---|---|
| Válido, con registros | Válido, con registros | Actualiza Procesos, OC y proveedores, si presentes | Contratos y relectura |
| Válido, **solo encabezado** | Válido, con registros | Actualiza OC/proveedores; **no escribe Procesos** | **Validado el 03-11** |
| Válido, con registros | Válido, **solo encabezado** | Actualiza Procesos/proveedores si presentes; **no escribe OC** | Prueba aislada sintética |
| Válido, vacío | Válido, vacío | Bloquea sin escribir | No reporta éxito |
| **Descarga, ZIP o parseo fallido** | Válido | **Actualmente bloquea la operación conjunta** | Pendiente aislamiento de falla técnica |
| Válido | **Descarga, ZIP o parseo fallido** | **Actualmente bloquea la operación conjunta** | Pendiente aislamiento de falla técnica |
| Válido | Registros con claves inválidas | Bloquea cuando la fuente tiene filas pero ninguna PK procesable | Evita pérdida silenciosa |

**Nota importante:** el código actual aísla **ausencia legítima de registros**, no todos los errores de disponibilidad, descarga, estructura, validación, cuotas o escritura. Si una fuente falla técnicamente, puede detener la carga de ambas; **no declarar que esto ya está resuelto**. Para cumplir el requisito completo se necesita un diseño adicional de transacciones y recuperación independiente por origen, con aprobación y pruebas específicas por el carácter protegido del proceso.

## 3. Contrato de publicación y workflow GitHub Actions

La publicación se alimenta desde las hojas MER verificadas, no descarga nuevamente los ZIP.

- `frontend-v2/data/catalogo-publico.json` es el manifiesto público para `procesos`, `ordenescompra`, `ofertas` y `resultados`.
- Cuando una entidad tiene **0 registros** y no ha sido alimentada todavía, su representación pública válida es un fragmento `0001.json` con el arreglo JSON vacío `[]` y conteo 0. El archivo debe estar **versionado y disponible en el checkout de Actions** antes de que el workflow recorra el manifiesto.
- **Incidente real del 03-11:** el catálogo de noviembre sí declaraba `data/partes/ofertas/2026-11/0001.json` y `data/partes/resultados/2026-11/0001.json`, pero estos faltaban en GitHub; la tarea `publicacion-v2-post-etl` falló con `FileNotFoundError` tras indexar las 8.180 OC. Los dos archivos `[]` se añadieron al repositorio. El reintento del job original continuó fallando por ausencia del mismo fragmento en su checkout; **no se ha acreditado todavía una ejecución nueva de derivados contra el commit corregido**. No se debe confundir **exportación de OC publicada** con **índices derivados validados y desplegados**.
- La implementación actual del workflow utiliza `set -euo pipefail` y un único job en serie: **un fallo en generación de cualquier entidad cancela la generación/publicación de los derivados de las demás**. Esto preserva integridad global, pero **todavía no satisface la tolerancia por entidad ante fallas técnicas**. No convertir los pasos a `continue-on-error` ni ocultar fallas.
- El contrato futuro deseado para tolerancia completa debe distinguir por entidad `VALIDADA`, `VACÍA_OFICIAL`, `ERROR_ORIGEN`, `ERROR_ESQUEMA`, `ERROR_PERSISTENCIA` y `PENDIENTE_PUBLICACIÓN`; conservar siempre los últimos derivados válidos de la entidad fallida y permitir publicar solo la entidad exitosa, **sin crear referencias inexistentes ni alterar contadores de otras entidades**. Requiere implementación y pruebas integrales separadas.
- **Una ejecución de Actions `success` con pasos omitidos no acredita publicación**. Verificar el estado de los pasos de derivados, commit Git y Pages.

## 4. Evidencia y controles obligatorios

**Evidencia productiva del 03-11-2026:** simulación de ZIP mensuales: licitaciones `CSV_SIN_REGISTROS`, OC `DISPONIBLE`, `OrdenesCompra=8180`, `Proveedores=3911`, `Procesos` no modificada. Ejecución real `--ejecutar` con `ORQUESTADOR OK`, `ultima_ejecucion.estado=EXITOSA`, `cobertura=PARCIAL_VERIFICADA`, 8.180 OC y 3.911 proveedores nuevos, 0 modificaciones. Catálogo público del mes con 8.180 OC y 0 procesos; no extrapolar cobertura total de noviembre.

**Pruebas aisladas:** `tests/test_etl_fuentes_independientes.py` y `.github/workflows/validar-etl-fuentes-independientes.yml`; cinco pruebas completadas exitosamente sin red, Sheets ni escrituras de producción. Estas pruebas **no** simulan un error HTTP, un ZIP corrupto, una escritura interrumpida o la publicación aislada de derivados: esas pruebas quedan pendientes para una ampliación posterior.

**Cada jornada validar por separado:**
- **Ubuntu:** ejecución a las 16:00, descarga+integridad de ZIP, conteos de staging, hojas efectivamente escritas, respaldos completos, relectura, estado por fuente y conciliación.
- **GitHub:** catálogo y todos sus fragmentos, conteos, generación de índices por entidad, validaciones previas al commit, commit de derivados y despliegue Pages.
- **API Compra Ágil:** workflow nocturno separado; ni éxito ni falla nocturnos sustituyen los indicadores de licitaciones y OC.

**Conservación/reversión:** no modificar horarios ni cron/timers; no borrar bitácoras, respaldos, fragmentos o hojas; usar los commits y el historial Git para revertir solo cambios autorizados si una prueba descubre regresión. Las tablas no alimentadas permanecen intactas.

## 5. Estado de cumplimiento

- **IMPLEMENTADO Y VALIDADO EN PRODUCCIÓN:** aislamiento de **CSV oficial vacío** en una de las dos fuentes durante carga Ubuntu.
- **IMPLEMENTADO, PERO PUBLICACIÓN DERIVADA NO AUTÓNOMA POR FUENTE:** separación de datos en catálogo y fragmentos; workflow aún conjunto y fail-fast.
- **NO IMPLEMENTADO:** continuidad independiente cuando una fuente descarga mal, no se puede parsear, viola contrato o su escritura a Sheets falla.
- **REGLA PARA FUTUROS CAMBIOS:** no afirmar «si falla cualquiera de las dos, la otra siempre se ejecutará» hasta validar fallas reales y simuladas en las dos rutas, persistencia y despliegue. El cambio adicional exige intervención específicamente autorizada en la línea base protegida.

**Documentos relacionados:** [línea base cron 16h](LINEA_BASE_PROTEGIDA_CRON_1600.md) · [política de protección](POLITICA_PROTECCION_CUATRO_PROCESOS.md) · [operación API](API_400_GITHUB_ACTIONS.md).

## 6. Cierre comprobado de publicación — 03/11/2026

**Causa exacta:** el primer job de derivados (#41710824306) usó un checkout donde faltaban los fragmentos vacíos de `ofertas` y `resultados` para noviembre que el catálogo ya referenciaba. Reintentar ese job con el SHA antiguo reprodujo el error. Se versionaron ambos `0001.json` como `[]` y se corrigió `.github/workflows/publicacion-v2-post-etl.yml` para ejecutar `checkout` sobre `main` vigente y dispararse también ante cambios en `frontend-v2/data/partes/**`, sin modificar los horarios ni los datos de Sheets.

**Resultado verificable:** workflow de derivados [#41712532138](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/41712532138) **success** en generación, validación y commit; índice de búsqueda de OC noviembre `conteo=8180`, perfiles `registros=8180`, analítica `registros=8180`. Supervisión posterior [#41712975889](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/41712975889) **success**. GitHub Pages [#41712975813](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/41712975813) completó **success** el paso de despliegue del frontend. Las verificaciones corresponden a Actions y repositorio; no constituyen una comprobación independiente de la caché HTTP del navegador del usuario.

**Pendientes distintos del despliegue:** la etiqueta de octubre continúa figurando `operativo` en el catálogo público mientras el catálogo privado ya la identifica como `historico`; la independencia frente a fallas técnicas (no solo CSV vacío) requiere implementación adicional. No repetir la carga de 8.180 OC para solucionar estos asuntos.

## 7. Continuidad desatendida por período — 03/11/2026

**Necesidad ratificada:** el sistema NO requiere seleccionar manualmente un mes en GitHub cada jornada. El reloj `America/Santiago` determina el mes para el cron diario; el catálogo privado `config/catalogo_sheets.json` identifica exactamente un `tipo=operativo`; y el exportador registra `ultima_exportacion.periodo` en el catálogo público. Los workflows de derivados y supervisión consumen ese período exportado y contrastan su autorización contra el catálogo privado, de modo que también puedan reconocer un cierre excepcional identificado expresamente. No se codifica `2026-11` en los workflows.

**Correcciones de recurrencia:**
- `scripts/exportar_mer_operativo_v2.py`: actualiza las etiquetas `historico/operativo` de cada período público de acuerdo con el catálogo privado, sin alterar conteos ni fragmentos históricos; escribe `ultima_exportacion` al completar una exportación.
- `scripts/ubuntu_publicar_v2_post_etl.sh`: incluye en el commit los fragmentos de **las cuatro entidades** para el mes, incluidos `ofertas/0001.json` y `resultados/0001.json` cuando están vacíos. Previene el fallo inaugural observado en noviembre.
- `.github/workflows/publicacion-v2-post-etl.yml`: lee el período de `ultima_exportacion` y conserva la comprobación de exportación fresca; no extrapola por sí solo el mes del reloj cuando hay una exportación identificada.
- `.github/workflows/verificar-publicacion-diaria-v2.yml`: contrasta período y clasificación contra el catálogo privado. Un `success` de pasos omitidos no acredita datos.
- `frontend-v2/data/catalogo-publico.json`: se corrigió la etiqueta de octubre de 2026 a `historico`, conservando noviembre como `operativo` y sus 8.180 OC.
- El gráfico de concursos muestra 0 para noviembre porque **el conjunto `Procesos` está vacío**, no porque el publicador ignore el mes. Las 8.180 OC aparecen en la entidad `ordenescompra`. No mezclar métricas de ambas fuentes.

**Controles de producción:** preservar el único cron Ubuntu y sus bloqueos, API nocturna y consolidación histórica. Estas correcciones no sustituyen la prueba real de rotación diciembre/enero ni hacen tolerante a errores técnicos por fuente a toda la cadena. Verificar ejecuciones GitHub y Pages luego del commit de sincronización.

## 8. Agregados de organismos compradores: reparación histórica y continuidad desatendida

**Hallazgo del 03/11:** los agregados históricos `frontend-v2/data/analitica/YYYY-MM/procesos.json` fueron publicados originalmente sin `organismos_procesos_unicos`, `procesos_unicos` ni `modalidades_unicas`. La columna «Organismos compradores» del frontend V2 estaba programada para **no mostrar importes duplicados por filas**, de modo que aparecía vacía sin filtro, mientras que los resultados de búsquedas temáticas sí incluían concursos únicos.

**Solución permanente:** `scripts/reparar_analitica_organismos_v2.py` recorre **todos los meses existentes en `catalogo-publico.json`**, contrasta conteo, presencia de campos, procesos únicos y suma de organismos; solo reconstruye las analíticas ausentes o incompatibles a partir de los **fragmentos públicos ya versionados**, sin acceso a Google Sheets ni descargas ZIP. El generador original `scripts/generar_analitica_v2.py` deduplica por código de proceso antes de agregar presupuesto y tipo de modalidad por organismo. **No suma varias veces un presupuesto por las ofertas**.

**Automatización:** `.github/workflows/reparar-analitica-organismos-v2.yml` se ejecuta ante cambios de su código, al terminar satisfactoriamente la publicación diaria y de lunes a viernes a las 19:15 de Chile (disparadores alternativos UTC-3/UTC-4); también permite un disparo manual excepcional. El checkout usa `main` vigente, publica por commit únicamente los agregados reconstruidos, y el workflow existente de Pages se dispara por cambios en `frontend-v2/data/analitica/**`. Si ningún agregado falta, registra `AGREGADOS_VIGENTES_SIN_CAMBIOS` y no crea commits ni despliegues innecesarios.

**Política:** no añadir meses fijos ni repetir las tareas históricas por rutina; cada nuevo mes queda automáticamente descubierto desde el manifiesto. Un mes sin registros de `Procesos` mantiene `organismos_procesos_unicos=[]` y contador cero: las OC no se convierten en concursos inventados.

**Estado de validación:** el disparo inicial y la regeneración histórica deben auditarse mediante logs de Actions, conteos JSON y resultado del despliegue Pages antes de declarar la reparación publicada. La programación y el código de reparación ya están en GitHub; **no cambia el cron de las 16:00 ni la API nocturna**.


**Validación productiva de reparación (03/11):** workflow [#41721120892](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/41721120892), resultado **success**. Los logs registran reconstrucción y validación de junio (80.898 procesos), julio (80.996), agosto (83.937), septiembre (79.376) y octubre (4.418); noviembre, con 0 procesos, ya tenía un agregado vigente y quedó sin cambios. El commit automático publicó cinco archivos de analítica. Los resultados concretos incluyen junio 1.983 organismos y octubre 868. La verificación de Pages posterior al commit debe constar por separado para acreditar su despliegue, no inferirse del push.


## 9. Navegación desde ranking de organismos compradores — 03/11/2026

El usuario aprobó enlazar los nombres de organismos compradores del ranking y del detalle `Concursos que componen cada barra` hacia la sección **Buscar**, manteniendo el período seleccionado y la entidad `Procesos`. Implementado en `frontend-v2/js/analitica-visual.js`, `frontend-v2/js/busqueda-global.js` y `frontend-v2/css/styles.css`.

La búsqueda usa los índices de la totalidad de fragmentos de **ese mes**, pero valida adicionalmente que el campo `organismo_comprador` coincida exactamente tras normalización de mayúsculas y tildes; no basta que el nombre se mencione en el título, nombre o código del proceso. Se restablecen los filtros Estado y Modalidad, se limita el alcance al mes, y se utiliza la paginación del buscador global (no el primer bloque de 1.000 registros). El nombre es un control con apariencia de hiperenlace y manejo de teclado. `Sin organismo informado` no crea un enlace ficticio.

No hay URLs por organismo ni períodos fijos; funciona en los nuevos meses publicados. No modifica ZIP, ETL, Sheets ni programación nocturna. La verificación definitiva exige comprobar la ejecución de Actions de frontend, la publicación Pages y una prueba de navegación visual con un organismo de varios procesos.


## 10. Corrección urgente de arranque tardío GitHub Actions — madrugada 04/11/2026

**Síntoma verificado:** el schedule `Compra Agil diaria 400 - cierre nocturno` no aparecía en la ventana nocturna de martes 03/11 a las 22:05. Los últimos disparos observados en días anteriores habían llegado sobre las 02:30 hora chilena y terminado con `success` pero con **todos los pasos de consulta en `skipped`** porque la guarda autorizaba exclusivamente inicios con `hour==22`.

**Corrección implementada:** `.github/workflows/api-compra-agil-400-actions.yml` utiliza `scripts/ventana_api_nocturna.py` (evaluación horaria local con `zoneinfo`, después del checkout). Se autoriza un inicio **entre las 22:00 y 04:59 de Chile**, pero únicamente si la fecha de la *jornada objetivo* corresponde a lunes–viernes. A las 22:00–23:59, objetivo=hoy. A las 00:00–04:59, objetivo=ayer. Así, iniciar el miércoles 04/11 a las 02:30 significa consultar el martes **03/11**, no miércoles, conservando el mes objetivo y los checkpoints. Desde las 05:00 el control omite la ejecución para no empezar nuevos lotes fuera de la ventana operativa. Los dos crons UTC (01:05/02:05) permanecen como alternativas estacionales; `concurrency` y la cola por jornada protegen los detalles ya confirmados.

**Pruebas CI:** `tests/test_ventana_api_nocturna.py` y `.github/workflows/validar-ventana-api-nocturna.yml`: nueve escenarios, que cubren 22:05/23:45, retrasos 02:30/04:45, 05:00 fuera de ventana, finales de semana y madrugada de cambio de mes. Ejecución inicial [#41765462484](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/41765462484) **success**. No se han realizado consultas productivas de API en esta prueba.

**Límite pendiente:** esto corrige la **guardia horaria**, no garantiza que GitHub genere efectivamente un disparo `schedule`; si GitHub lo omite o ejecuta después de las 05:00, no habrá consulta. Tampoco recupera automáticamente el día 02/11 si solo procesa la jornada objetivo 03/11: esa recuperación requiere un mecanismo explícito de jornadas pendientes verificadas. En un cruce de mes, el motor todavía impide cargar un mes archivado sin autorización excepcional. No interpretar `success` con `skipped` como ejecución de la API.


## 11. Incidente Pages del 04/11/2026 tras cron Ubuntu 16:00 — corregido

**Síntoma:** después de la publicación del ETL a las 16:03 Chile, el catálogo de `frontend-v2/data/catalogo-publico.json` indicaba **16.197 órdenes de compra de noviembre** (8.180 previamente). `Publicacion V2 posterior al ETL Ubuntu` completó bien [#41893167030](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/41893167030), pero dos intentos de Pages [#41893260157](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/41893260157) y [#41893337124](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/41893337124) fallaron. El primero permaneció en `updating_pages` hasta el timeout del action (10 minutos); el segundo quedó cancelado. Las comprobaciones de integridad y la subida del artefacto sí habían sido satisfactorias.

**Causa operativa:** disparos duplicados `workflow_run` por la publicación principal y la reparación de analítica, más empaquetado de todo el repositorio en lugar del sitio.

**Corrección focalizada:** `.github/workflows/preview-frontend-v2.yml` eliminó el disparo `workflow_run` directo desde `Publicacion V2 posterior al ETL Ubuntu`, porque **ese workflow ya dispara `Reparar analítica de organismos por período`**, y ésta dispara Pages tras terminar; se conservan el resto de triggers aprobados. La publicación ahora construye `_pages` temporal con `index.html` V1, `data/observatorio.json` V1, y `frontend-v2/` completo, preservando rutas y cobertura histórica, pero excluyendo el repositorio de código, documentación y otros datos que no consume el sitio. Se conserva el control de integridad antes de publicar y la serialización del deployment.

**Verificación productiva:** ejecución [#41898390466](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/41898390466) **success**; todos los pasos correctos, incluido `actions/deploy-pages@v4` con mensaje `Reported success!`. El paquete preparado contenía 41.121 archivos y 1,4 GB sin comprimir; artefacto comprimido de 256.820.537 bytes. Esto no garantiza el mismo desempeño si sigue creciendo el histórico: la dimensión de datos y el número de archivos siguen siendo un riesgo que debe monitorearse aparte.

**Separación de responsabilidades:** no se modificaron Ubuntu cron 16:00, API Compra Ágil, Sheets, archivos históricos ni rotación/conciliación. La lectura HTTP independiente del catálogo publicado no pudo verificarse desde este entorno; la certificación final respaldada aquí es la publicación exitosa registrada por GitHub Actions.

**Reversión:** restaurar la versión anterior de `.github/workflows/preview-frontend-v2.yml` desde el commit previo, aunque ello reintroduciría los disparos duplicados y el artefacto general del repositorio. No revertir ETL ni datos.
