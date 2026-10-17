# Observatorio de Mercado Público — Estado y operación de marcha blanca

**Corte documental:** 16 de octubre de 2026. **Estado:** desarrollo operativo en validación; no se considera producción.  
**Repositorio:** [MercadoPublico-Inteligencia](https://github.com/juliopez/MercadoPublico-Inteligencia).

## 1. Objetivo y arquitectura

El observatorio permite consultar procesos de licitación, Compra Ágil, ofertas, resultados y órdenes de compra con información oficial de ChileCompra.

```text
ChileCompra API V1 / V2
        ↓
ETL ejecutados manualmente en GitHub Actions
        ↓
Google Sheets — fuente de datos operativa
  Procesos | Ofertas | Resultados | OrdenesCompra
        ↓ (publicación manual independiente)
scripts/publicar_observatorio.py
        ↓
data/observatorio.json
        ↓
GitHub Pages — index.html
```

**No hay cron ni actualización automática de los datos.** Abrir el frontend no consulta directamente ChileCompra ni modifica Google Sheets. No se deben publicar tokens o credenciales.

- [Base de datos de Google Sheets](https://docs.google.com/spreadsheets/d/1y81QaPy37APkBwxlYrKyE66_1ECdhL87GyWNitTfHr4/edit)
- [Workflow de operaciones manuales](../../actions/workflows/marcha-blanca-manual.yml)
- [Workflow de despliegue del frontend](../../actions/workflows/pages.yml)

## 2. Decisiones vigentes de la marcha blanca

1. El operador **ejecuta manualmente** cada proceso y elige la fecha `AAAA-MM-DD`. Sin fecha o con fecha futura/inexistente, no comienza la extracción.
2. Se recomienda ejecutar primero **Licitaciones**, luego **Compra Ágil**, después **Órdenes de compra** y finalmente **Publicar**; comprobar cada ejecución antes de la siguiente.
3. El workflow contiene cinco operaciones: `licitaciones`, `compra_agil`, `ordenes_compra`, `publicar`, `completa`. La fecha es obligatoria incluso para `publicar`, aunque en esa opción **no filtra** los datos publicados.
4. Las ejecuciones del mismo workflow comparten un grupo `concurrency` y no deben ejecutarse simultáneamente. No se cancela automáticamente una ejecución anterior.
5. El orquestador tiene **hasta tres intentos por componente**, separados por 45 segundos si falla. Dentro del workflow, `API_MAX_ATTEMPTS=1` evita que cada consulta individual agregue otros intentos.
6. Los ETL insertan/actualizan por claves; volver a consultar una fecha no debería duplicar procesos. **Falta validar la idempotencia integral de ofertas, resultados y órdenes.**
7. `completa` publica solo cuando terminan satisfactoriamente sus etapas. Los ETL individuales **no publican** automáticamente: luego se usa `publicar`.
8. La carga histórica masiva es otro procedimiento. Se acordó comenzar con la base vacía; no se conservó un respaldo adicional de su contenido por petición del propietario.

## 3. Componentes actuales

| Componente | Archivo principal | Función | Validación |
|---|---|---|---|
| Licitaciones (procesos) | `scripts/sync_chilecompra_sheets.py` | API V1, listado por fecha, escritura en `Procesos` | Primera carga informada en log; ver §5 |
| Licitaciones (adjudicaciones) | `scripts/sync_resultados_licitaciones.py` | Consulta detalles por código y alimenta `Resultados` cuando existe información | **Incidencia HTTP 429** |
| Compra Ágil (procesos) | `scripts/sync_chilecompra_sheets.py` | API V2, listado paginado por fecha | Pendiente de prueba integral |
| Compra Ágil (cotizaciones/selecciones) | `scripts/etl_multiproceso_manual.py` | Consulta detalle de procesos registrados; escribe en `Ofertas` y `Resultados` | Pendiente de prueba integral |
| Órdenes de compra | `scripts/sync_ordenes_compra_sheets.py` | API V1, listado por fecha y detalle por código; escribe en `OrdenesCompra` | Pendiente de prueba integral |
| Publicador | `scripts/publicar_observatorio.py` | Lee cuatro hojas y genera JSON público | Publicación vacía comprobada visualmente por el propietario |
| Frontend | `index.html` | Consulta pública, filtros, detalle y vista inicial de OC | Funcional con base vacía; ayudas contextuales incorporadas |
| Operación | `.github/workflows/marcha-blanca-manual.yml` | Cinco opciones manuales | Primer caso de licitaciones en curso al momento del último reporte |
| Despliegue de sitio | `.github/workflows/pages.yml` | Publica frontend manualmente | Despliegue del estado vacío confirmado por el propietario |

**Los dos workflows anteriores son los únicos presentes en `.github/workflows/`**, tras la limpieza. Pueden permanecer scripts auxiliares de pruebas en `scripts/`; su existencia no significa que se ejecuten automáticamente.

## 4. Base de datos y contrato de campos

Libro principal: `Observatorio Mercado Público — Base de Datos`.

| Hoja | Columnas | Uso |
|---|---:|---|
| `Procesos` | 16 | Procesos de Licitación y Compra Ágil |
| `Ofertas` | 7 | Proveedores y cotizaciones/ofertas obtenidas |
| `Resultados` | 10 | Selecciones y adjudicaciones, sin confundirlas con OC verificadas |
| `OrdenesCompra` | 10 | Órdenes públicas; entidad transaccional separada |
| `Control` | Encabezados operativos | Seguimiento y auditoría |
| `Indicadores` | Encabezados operativos | Indicadores derivados |
| `Órdenes de compra agosto 2026 (resumen)` | 10 | Hoja histórica separada; vaciada durante el reinicio |

Las tres primeras hojas contienen **33 columnas en total (16 + 7 + 10)**; `OrdenesCompra` mantiene su estructura adicional. El publicador genera las colecciones `procesos`, `ofertas`, `resultados` y `ordenescompra` dentro de `data/observatorio.json`.

**Reinicio confirmado:** se vaciaron los registros de todas las hojas, conservando sus encabezados; también se reinició el JSON público. El propietario confirmó que el frontend quedó sin registros antes de ejecutar la primera carga de prueba. Este estado de referencia **ya puede cambiar** cuando se ejecutan ETL.

## 5. Primera prueba manual — 14 de octubre de 2026

**Observación parcial de GitHub Actions #1, aportada durante su ejecución; NO es un resultado final:**

- Operación: `licitaciones`; fecha de consulta: `2026-10-14`.
- Log del listado inicial: `API_V1_LICITACIONES 2026-10-14 registros 1221`.
- Log de escritura: `Sincronizados: 0 actualizados, 1221 nuevos.`
- La fase posterior `licitaciones_resultados` comenzó a consultar detalles por código, y recibió **múltiples respuestas HTTP 429 (Too Many Requests)**.
- El estado definitivo del workflow, la cantidad final de adjudicaciones cargadas y la integridad en Sheets **aún no estaban confirmados** al documentar esta observación.
- **No modificar, reiniciar ni lanzar otros ETL mientras la ejecución observada siga activa.** Esperar su resultado y después revisar los datos en Sheets.

**Diagnóstico:** consultar gran cantidad de detalles individualmente puede exceder los límites de la API. El ETL actual continúa evaluando otros códigos después de un 429 y no aplica una pausa global; por ello no se debe dar por validada esta fase.

**Corrección pendiente, sujeta a evaluación tras el fin del proceso:** tratar 429 como limitación de frecuencia, respetar `Retry-After` si existe, introducir control de ritmo y reanudación de pendientes por fecha/código, priorizar procesos que requieren actualización y no repetir masivamente consultas rechazadas. Conservar procesos previamente incorporados.

## 6. Límites conocidos y criterios de aceptación

- Las API de listado por fecha no garantizan que se recuperen **todos los cambios posteriores** de procesos antiguos. El ETL de adjudicaciones consulta además licitaciones marcadas como cerradas o adjudicadas, pero **esa cobertura todavía no está validada**.
- La API de detalle de licitaciones no garantiza todas las ofertas individuales. **No crear ofertas ni adjudicaciones ficticias**; los históricos oficiales permiten complementar información según disponibilidad.
- La selección de una cotización en Compra Ágil no es equivalente a una orden de compra o contrato comprobado.
- No está validado el comportamiento del frontend con un volumen histórico elevado; el publicador aún genera **un único JSON**.
- Los secretos se mantienen en GitHub Actions: `CHILECOMPRA_TICKET`, `GOOGLE_SERVICE_ACCOUNT_JSON`. La variable `GOOGLE_SHEET_ID` identifica la base. Nunca copiarlos a `index.html`, logs o archivos publicados.
- La marcha blanca se considerará exitosa solo al verificar por categoría las cantidades de registros, claves únicas, correspondencia entre hojas, ausencia de datos espurios y publicación correcta.

## 7. Operación y recuperación

Para procesar una fecha: [abrir Actions](../../actions/workflows/marcha-blanca-manual.yml), seleccionar `Run workflow`, elegir operación y escribir fecha. Revisar los logs hasta que finalice. Si falla una categoría, **no repetir inmediatamente un lote de consultas HTTP 429**; diagnosticar antes de reintentar.

Una vez validados los datos en Sheets, seleccionar `publicar` para generar el JSON y desplegar Pages. Si solo cambia el HTML, utilizar `pages.yml`. Una publicación manual no debe interpretarse como validación de los ETL.

**Referencia de recuperación del código:** rama `respaldo-pre-limpieza-marcha-blanca-20261016`. No se generó un respaldo nuevo de los datos de Google Sheets durante el reinicio.


## 8. Corrección transversal de control de API (16-10-2026, posterior a la primera cancelación)

**Implementación en código, pendiente de prueba operativa.** Se modificaron `api_retry.py`, los ETL de detalles de licitaciones y Compra Ágil, el ETL de órdenes de compra y el workflow manual.

- El cliente compartido usa un intervalo mínimo configurable (`API_MIN_INTERVAL_SECONDS`, predeterminado 1,5 s) entre consultas **dentro de cada proceso Python**. No representa una tasa autorizada ni garantiza que la API no limite solicitudes.
- HTTP 429 provoca una detención inmediata del lote, registra `Retry-After` si se informa y crea la señal `.api_rate_limited`. El workflow detecta esa señal y **no inicia el segundo/tercer intento ni otras categorías**. La señal es temporal dentro del runner, no contiene credenciales.
- En `Control!M:P` se registran checkpoints de detalle de licitaciones; en `Control!Q:T`, checkpoints de detalle de Compra Ágil; y en `Control!U:X`, checkpoints de órdenes de compra. Se emplean registros por fecha y código para evitar repetir los ítems completados en una reejecución manual.
- El complemento de licitaciones persiste cada adjudicación antes de anotar su checkpoint; el detalle de Compra Ágil guarda los avances del lote procesado; las órdenes de compra guardan los datos recuperados antes de informar un corte por 429.
- Los errores distintos de 429 aún requieren inspección de logs y, si corresponde, ejecución manual con la misma fecha; los checkpoints no garantizan que un proceso previamente consultado nunca cambie de estado en el futuro.
- **Atención:** los límites concretos de ambas API son desconocidos. No se han ejecutado pruebas de carga posteriores a este cambio y no corresponde considerar validadas aún la cobertura completa, la integración del flujo ni la actualización de estados futuros.


## 9. Revisión de adjudicaciones incompletas tras la tercera ejecución

La ejecución manual n.º 3 se detuvo correctamente ante HTTP 429. Antes de detenerse dejó dos filas en `Resultados` con fecha, pero sin proveedor ni monto. Estas filas **no deben considerarse adjudicaciones confirmadas**.

La versión corregida de `sync_resultados_licitaciones.py` exige proveedor y monto explícitos antes de insertar un nuevo resultado, registra `pendiente_datos` cuando falta alguno de los dos y no interpreta checkpoints antiguos `completo` como suficientes si no existe un resultado con ambos campos. Una reejecución de la misma fecha puede consultar esos códigos pendientes, y una fecha posterior permite revisar adjudicaciones ya registradas. **Esto no significa que la API entregue siempre el proveedor o el monto:** cuando no los entrega se preserva la incertidumbre.

**Pendiente operativo:** revisar las dos filas incompletas ya existentes en `Resultados` (`1017312-6-LR26`, `1030-20-LE26`); esta corrección de código no las borró ni las convirtió en resultados confirmados. No se activó workflow ni se realizaron consultas adicionales a ChileCompra.
