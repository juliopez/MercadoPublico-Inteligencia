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
