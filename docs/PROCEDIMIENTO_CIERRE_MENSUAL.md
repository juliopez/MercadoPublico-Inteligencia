# Procedimiento de cierre mensual — MER v2

**Estado:** diseño operativo aprobado como documento técnico, **sin ejecución**. La hoja operativa del mes en curso contiene seis entidades MER v2 y recibe ZIP de Licitaciones y Órdenes de Compra mediante Ubuntu/cron y Compra Ágil mediante un flujo independiente aún pendiente. El histórico mensual definitivo se materializa **días después del cierre**, una vez disponibles los archivos oficiales.

## Ciclo mensual
1. **Operación diaria:** escribir exclusivamente en `MER_AAAA_MM_OPERATIVO` mediante ETL ZIP para Licitaciones/OC y eventual API de Compra Ágil, con inserción idempotente por PK, logs, reintentos limitados y auditoría de errores. No modificar históricos cerrados.
2. **Corte:** transcurridos los últimos días del mes, fijar fecha/hora del cierre lógico; pausar escrituras de ese período y crear respaldo integral de la hoja operativa.
3. **Fuentes oficiales:** obtener ZIP oficiales del mes para licitaciones, Compra Ágil y OC; comprobar correspondencia del período y completar manifiesto con nombres, tamaño, SHA-256 y fecha de obtención. No inferir que una OC se corresponde temporalmente con el mes de publicación del proceso.
4. **Preparar:** ejecutar el importador generalizado para producir seis CSV MER v2 con informe y auditoría. No escribir directamente el paquete hasta revisar discrepancias, especialmente proveedores, selección de ofertas y OC.
5. **Conciliar:** comparar instantánea operativa y fuente oficial por claves; priorizar las fuentes oficiales para valores históricos, preservar registros que todavía carezcan de resolución y registrar diferencias/duplicados. Las 8.275 OC fuera de corte observadas en septiembre muestran que un enlace COT–OC fuera del mismo mes es legítimo y **no se debe forzar**.
6. **Materializar histórico:** crear nueva hoja `MER_AAAA_MM` en `01_Historicos_MER`; completar y verificar las seis entidades mediante carga autorizada, respaldada y recuperable.
7. **Auditoría bloqueante:** confirmar encabezados, conteos, PK, FK a Procesos/Ofertas/Proveedores, consistencia oferta–resultado, unicidad de pares COT–OC, estados de OC y origen por período; separar errores de observaciones aceptadas.
8. **Publicación:** registrar el Sheet ID histórico en catálogo; actualizar exclusivamente los JSON compatibles con contrato del frontend mediante consolidador, validar sitio y despliegue por etapas.
9. **Rotación:** tras aprobación del histórico y su publicación, reemplazar referencia del ETL a un **nuevo archivo operativo** del mes siguiente. No borrar el archivo operativo anterior hasta verificar el histórico y su respaldo.
10. **Trazabilidad:** documentar respaldo, paquetes y hashes, resultados de auditoría, conflictos, commit GitHub y responsables/fechas.

## Reglas obligatorias

- Los históricos son inmutables tras el cierre, salvo proceso de corrección auditado y respaldado.
- Una selección marcada en histórico COT no es necesariamente una adjudicación jurídica; nunca forzar `validado=true`.
- No eliminar archivos ni alterar ETL productivos o frontend sin validación específica.
- Evitar cargas simultáneas al mismo destino y escrituras sobre rangos que puedan contener registros anteriores.
- Nunca trasladar automáticamente la Google Sheets operativa «tal cual» sin confrontar con el histórico oficial.
- No asumir que Google Sheets de un mes entero cabrá: comprobar el límite de 10 millones de celdas **por archivo** y bloquear sobrepasos.
- Meses extraordinarios a cargar inicialmente: junio, julio y agosto de 2026; septiembre ya cerrado. Octubre y sucesivos siguen el ciclo operativo descrito.

## Pendientes técnicos para automatización real
1. Completar el flujo de Compra Ágil por API v2 de forma independiente de los ZIP de licitaciones y OC.
2. Diseñar conciliador oficial/API y cargador con resolución de colisiones y datos actualizados.
3. Implementar disparador de cierre sujeto a disponibilidad de históricos y auditorías; **no** cierre ciego el día primero.
4. Implementar consolidador y publicación transaccional JSON; pruebas integrales antes de activar.

## Primer avance de automatización del cierre (octubre–noviembre de 2026)

Se implementó [`scripts/monitorear_cierre_mensual.py`](../scripts/monitorear_cierre_mensual.py): a partir del día 1 del mes siguiente comprueba **sin descargar ZIP enormes** la disponibilidad HTTP de los tres archivos oficiales del mes anterior y genera `salida_operativa/cierre_candidato_AAAA-MM.json`. Nunca cambia nombres, ubicaciones, permisos, catálogos ni datos de Google Sheets; tampoco adjudica ni infiere verificación jurídica.

Ejecutar en Ubuntu **a partir de noviembre**:
```bash
.venv/bin/python scripts/monitorear_cierre_mensual.py
```

El resultado `FUENTES_DISPONIBLES_REVISION_MANUAL_PENDIENTE` significa únicamente que las tres URL responden 200. **No significa que el mes esté conciliado ni cerrado.** Deben descargarse y auditarse los seis CSV de la última versión oficial, revisar claves y discrepancias, obtener aprobación y recién entonces convertir la hoja a histórico. Si falta COT, reporta `ESPERANDO_FUENTES` sin bloquear la operación del mes nuevo. Evitar ejecutar el monitor antes de noviembre porque la fuente histórica anterior de septiembre ya está cerrada.

El monitor no está agregado al cron aún. La automatización de conciliación/archivado está pendiente; esta separación deliberada impide cerrar a ciegas o borrar los registros de octubre cuando aún falten ofertas.

## Orquestador de preparación — ejecución el día 10

**Implementado:** `scripts/orquestar_cierre_mensual.py`. Inicio previsto **el día 10 de cada mes, para el mes anterior**, con zona horaria America/Santiago. No se ha instalado un nuevo cron ni se ha ejecutado la descarga de cierre. No se ha ejecutado un traslado real.

### Etapas del nuevo script

1. **Precondiciones:** fecha a partir del día 10, período inmediatamente anterior registrado como `operativo`, mes vigente con su propia hoja, sin referencias excluidas.
2. **Descarga oficial:** tres URLs del catálogo `config/fuentes_descarga_mensual.json`. Se usan `*.partial` temporales y solo se conservan ZIP completos con CRC válido, SHA-256 y al menos un CSV; se reutilizan ZIP previos verificados en reintentos.
3. **Importación histórica:** reutiliza `scripts/importador_historicos_v2.py`, que genera seis CSV, staging SQLite e `informe.json` con recuentos y controles básicos, incluidas observaciones de vínculos fuera del corte.
4. **Estado persistente:** `~/.local/share/mercadopublico/cierres/AAAA-MM/estado_cierre.json`. Registra `DESCARGANDO`, `IMPORTANDO`, `BLOQUEADO` o `LISTO_PARA_CONCILIAR`; no marca `CERRADO`.
5. **Barrera obligatoria:** `LISTO_PARA_CONCILIAR` **no autoriza escrituras ni traslado**. Faltan reconciliar diferencias frente a la Google Sheets operativa, auditar PK/FK y coberturas, comprobar espacio disponible para 10 millones de celdas, respaldar los seis contenidos, cargar de manera recuperable, verificar lectura posterior y autorizar cierre.
6. **Traslado futuro:** tras las condiciones anteriores, mover el MISMO archivo por API Drive (sin clonarlo), renombrar, verificar nuevo directorio y permisos, cambiar catálogo de `operativo` a `historico` y registrar evidencia. Se debe poder recuperar una actualización parcial entre Drive y GitHub. La cuenta de servicio de Ubuntu podría carecer de permisos Drive para mover archivos; eso debe resolverse explícitamente.

### Invocación manual a partir del 10 de noviembre de 2026

```bash
.venv/bin/python scripts/orquestar_cierre_mensual.py
```

Este comando efectúa descargas y procesamiento local **pero nunca escribe en Sheets ni altera carpetas**. Los ZIP podrían no estar todavía publicados el día 10; entonces el proceso queda `BLOQUEADO`, conserva descargas verificadas y permite reintento. La publicación de una URL HTTP 200 no asegura completitud semántica ni resultados definitivos: se mantienen las validaciones de auditoría anteriores.

**Decisión pendiente de calendario:** hora concreta de lanzamiento (el usuario especificó día 10, no hora) y política de reintentos tras fallos. No programar el script hasta disponer de pruebas offline y del cargador conciliado seguro. El cron diario del ETL vigente permanece independiente.

**Actualización del diseño de materialización:** el procedimiento inicial proponía crear una nueva hoja histórica. Se prioriza ahora, conforme a la decisión del proyecto, **consolidar la hoja operativa existente y trasladarla conservando su ID**, siempre que las seis tablas sean auditables y la carga reconciliada. Si no cabe en los límites de Sheets o no se cumple una validación, detener y revisar alternativa sin perder el origen.

## Conciliador de seis tablas — segunda etapa (solo lectura)

Se añadió `scripts/conciliar_cierre_mensual.py`, junto con una prueba unitaria independiente de Google (`tests/test_conciliar_cierre_mensual.py`). El conciliador compara las **seis tablas** del paquete SQLite generado por el importador histórico contra la Google Sheets operativa del período anterior. Lee mediante `spreadsheets.readonly` y **no solicita permiso de escritura**.

Por cada tabla clasifica registros:
- **nuevos:** presentes en el histórico oficial, ausentes del operativo.
- **modificados:** misma PK, valores distintos.
- **sin_cambios:** misma PK y todos los valores idénticos.
- **solo_operativo:** presentes en la Google Sheets pero ausentes del paquete histórico; **no eliminar automáticamente**.

Valida la identidad del mes, disponibilidad de `preparado.sqlite` e `informe.json`, cabeceras, unicidad de PK, recuentos e integridad de filas, con ejemplos acotados de claves. Las diferencias no implican automáticamente errores ni aprobación de un cambio: deben revisarse antes de escribir.

### Ejecución prevista después del 10 de noviembre

```bash
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/mercadopublico/servicio-google.json"
.venv/bin/python scripts/orquestar_cierre_mensual.py
.venv/bin/python scripts/conciliar_cierre_mensual.py --periodo 2026-10 --paquete "$HOME/.local/share/mercadopublico/cierres/2026-10/preparados"
```

Salida: `~/.local/share/mercadopublico/cierres/2026-10/conciliacion.json`. **No ejecutar hoy**: solo el mes anterior puede conciliarse y no antes del día 10. Ejecutar las pruebas locales antes:

```bash
.venv/bin/python -m unittest discover -s tests -p 'test_conciliar_cierre_mensual.py'
```

La prueba anterior cubre clasificación de nuevas, modificadas, iguales y solo operativas, pero el script completo **aún no ha sido probado contra la Google Sheets de octubre**. El cron mensual continúa deshabilitado; objetivo: prueba supervisada 10 de noviembre y activación tentativa el 10 de diciembre tras aprobación.

La próxima etapa será decidir reglas por tabla y crear un cargador transaccional con respaldo, protección ante reintentos, auditoría completa y prueba de lectura final; el traslado Drive y actualización GitHub se harán solamente al terminar todas esas etapas.

## Política conservadora para aplicar diferencias — tercer avance

Se incorporó `scripts/planificar_carga_cierre.py`, que **solo lee** `conciliacion.json` y genera `plan_carga_cierre.json`. Requiere seis tablas y valida que sus cuatro clases sumen los totales histórico y operativo; no conecta con Google Sheets/Drive ni cambia catálogo.

- **Nuevos:** candidatos a insertar por PK tras aprobar cobertura y auditoría.
- **Modificados:** candidatos a actualizar; deben revisarse diferencias por campo. La selección histórica de una oferta no constituye adjudicación verificada.
- **Sin cambios:** no requiere escritura.
- **Solo operativos:** preservar, no borrar por falta de correspondencia en ZIP mensual.
- **Vínculos COT–OC fuera de período:** observación, no necesariamente error. Ambigüedades de selección deben quedar advertidas.
- El plan termina obligatoriamente con `autorizado_para_escribir=false` y `autorizado_para_mover=false`. No constituye orden de carga ni aprobación de cierre.

Pruebas offline en `tests/test_planificar_carga_cierre.py` cubren conteos incoherentes, ausencia de tablas y preservación de registros solo operativos. **Pendiente ejecutarlas en Ubuntu; no se ha realizado una prueba integral con octubre.**

Una vez disponible la conciliación en noviembre, generar el plan:

```bash
.venv/bin/python scripts/planificar_carga_cierre.py \
  --conciliacion "$HOME/.local/share/mercadopublico/cierres/2026-10/conciliacion.json"
```

### Barreras pendientes antes de activar escritura/traslado

1. Contrastar valores modificados a nivel de columna y definir reglas de precedencia por entidad, incluyendo semántica de resultados y proveedores.
2. Realizar auditoría referencial completa, integridad de los seis conjuntos y dimensión del destino para evitar límite de celdas.
3. Respaldar todo el operativo con hashes/CRC utilizando `respaldo_local()` ya desarrollado.
4. Implementar aplicador idempotente, relectura y comprobación post-escritura con manejo de ejecución parcial y recuperación.
5. Validar permisos Google Drive para traslado del archivo con mismo ID y transición del catálogo de forma recuperable.
6. Validación supervisada el 10 de noviembre; si resulta aprobada, recién instalar el cron mensual para comenzar 10 de diciembre.

**No modificar el ETL diario ni cron vigente.** No activar cierres mientras existan controles pendientes.

## Cuarta etapa: simulación de carga bloqueante

Se añadió `scripts/simular_carga_cierre.py`. Contrasta el catálogo, `estado_cierre.json`, `plan_carga_cierre.json`, `informe.json`, los seis CSV y el número de filas de cada tabla del SQLite preparado. Produce un informe con SHA-256 de los CSV y operaciones candidatas, **sin abrir Google Sheets ni realizar escrituras, respaldos de hojas o traslados**.

**Secuencia de ejecución supervisada a partir del día 10 de noviembre:** preparar con `orquestar_cierre_mensual.py`, ejecutar `conciliar_cierre_mensual.py`, generar el plan con `planificar_carga_cierre.py` y finalmente correr:

```bash
.venv/bin/python scripts/simular_carga_cierre.py \
  --periodo 2026-10 \
  --paquete "$HOME/.local/share/mercadopublico/cierres/2026-10/preparados" \
  --plan "$HOME/.local/share/mercadopublico/cierres/2026-10/plan_carga_cierre.json" \
  --estado "$HOME/.local/share/mercadopublico/cierres/2026-10/estado_cierre.json"
```

**Advertencia:** este paso es un simulador de precondiciones, **no el cargador de escritura definitivo**. No se debe describir como cierre listo para automatizar. Antes de habilitar escritura quedan pendientes política campo por campo, auditoría referencial ampliada, respaldo integral, idempotencia/reintentos, read-back, recuperación de fallos, y permisos Drive + catálogo. La ejecución programada del cierre continúa reservada para diciembre, sujeta a prueba integral supervisada en noviembre. No se ha cambiado el cron diario ni el frontend.

## Quinta etapa — motor de carga conservador (octubre 2026)

Código `scripts/motor_carga_cierre.py`: añade una política formal para registros del paquete MER v2 y comprueba coherencia de informes y SHA-256 de los seis CSV. El motor **no se conecta a Google ni escribe en la hoja**. Se mantiene el bloqueo mientras no existan precedencias por campo, auditoría final y estrategia probada de recuperación.

La función `simulacion()` ensaya localmente, sobre dos bases SQLite separadas, insertar solamente PK nuevas mediante `INSERT OR IGNORE`; preserva registros modificados y aquellos ausentes del ZIP. La operación es repetible sin duplicar claves (idempotencia). Pruebas unitarias en `tests/test_motor_carga_cierre.py`. **Pruebas pendientes de ejecución en Ubuntu**.

Para probar el motor offline:
```bash
.venv/bin/python -m unittest discover -s tests -p 'test_motor_carga_cierre.py'
```

Para inspeccionar el plan del mes anterior cuando estén sus archivos conciliados (a partir del día 10):
```bash
.venv/bin/python scripts/motor_carga_cierre.py \
 --paquete "$HOME/.local/share/mercadopublico/cierres/2026-10/preparados" \
 --conciliacion "$HOME/.local/share/mercadopublico/cierres/2026-10/conciliacion.json" \
 --plan "$HOME/.local/share/mercadopublico/cierres/2026-10/plan_carga_cierre.json"
```

**Límite de la etapa:** esto no equivale a un cargador remoto de producción. No se ha implementado aún reconciliación de campos modificados, operaciones Google Sheets con verificación final, rollback auditado ni traslado Drive/GitHub. No activar el cron mensual antes de completar y probar tales componentes. El ETL diario existente permanece independiente.

## Sexta etapa: evidencia vinculada y control de cambios

Se agregó `scripts/vincular_evidencia_cierre.py`. Verifica que período, Sheet ID y conteos sean coherentes entre catálogo, estado de preparación, informe del importador, conciliación y plan de carga. Calcula SHA-256 de los seis CSV, SQLite y cinco documentos de control; genera `evidencia_vinculada.json`. Si uno de esos insumos cambia después, su huella también cambiará y deberá repetirse la revisión. El módulo **no puede escribir en Google Sheets ni mover archivos**.

Prueba offline: `python -m unittest discover -s tests -p 'test_vincular_evidencia_cierre.py'`.

**Pendiente crítico:** falta implementar y probar una segunda comprobación de estas mismas huellas inmediatamente ANTES de cualquier escritura real y de una autorización explícita e independiente. Asimismo, el contenido operativo de Sheets puede cambiar después de la conciliación: se requiere relectura remota o sello verificable de estado previo. Hasta resolverlo, no activar un cargador remoto ni un cierre desatendido. Este módulo es un avance de seguridad, no un cierre completo.

No se ejecutaron las pruebas en Ubuntu, no se habilitó cron mensual y no se modificó frontend, Drive ni Sheets.

## Séptima etapa: revalidación del contenido operativo antes del cierre

El conciliador `scripts/conciliar_cierre_mensual.py` registra ahora `sha256_operativo` por tabla. La huella se calcula sobre **todas las filas y todos los campos**, ordenando las PK para ser insensible al orden de filas. El nuevo `scripts/revalidar_operativo_cierre.py` vuelve a leer las seis pestañas con permisos de **solo lectura**, verifica el Sheet ID del catálogo, los conteos y las huellas contra la conciliación original.

El cierre se **bloquea** si una tabla cambia, si falta su huella porque el informe procede de una versión antigua o si una pestaña presenta encabezados o PK incompatibles. Una coincidencia de conteos no sustituye la coincidencia de contenido. No se eliminan datos, no se escribe en Sheets y no se mueve ni renombra ninguna hoja.

### Pruebas locales
```bash
.venv/bin/python -m unittest discover -s tests -p 'test_revalidar_operativo_cierre.py'
```

### Uso previsto después del 10 de noviembre
```bash
.venv/bin/python scripts/revalidar_operativo_cierre.py \
 --conciliacion "$HOME/.local/share/mercadopublico/cierres/2026-10/conciliacion.json"
```

La lectura remota debe realizarse inmediatamente antes de una carga autorizada. **No equivale a una transacción**: otro escritor aún podría modificar Sheets después de la comprobación. Antes de habilitar el cargador real falta implantar exclusión mutua con el flujo de escritura, auditoría final, respaldo de las seis tablas, política para registros modificados, restauración y verificación posterior.

**Estado:** código publicado sin prueba de integración sobre octubre; cron diario sin cambios y cron mensual sin instalar. Primera validación supervisada el 10 de noviembre.

## Octava etapa: exclusión mutua entre ETL diario y preparación del cierre

El ejecutor **diario** `scripts/ubuntu_etl_dos_fuentes.sh` ahora adquiere `logs/.mer_escritura_compartida.lock` mediante `flock -n`, además de conservar su bloqueo propio `logs/.etl_dos_fuentes.lock`. El preflight supervisado `scripts/ubuntu_preflight_cierre.sh` adquiere **el mismo archivo de bloqueo** antes de volver a leer las seis tablas, verificar las huellas contra la conciliación, comprobar los insumos y generar evidencia; lo mantiene hasta terminar. No ejecuta carga real ni traslado.

El orden de bloqueo del ejecutor diario es siempre compartido → específico. El flujo de cierre toma únicamente el compartido. La exclusión funciona solamente entre procesos locales que **respeten ese mismo bloqueo** en la misma máquina/ruta; no protege contra cambios manuales en la web, otras máquinas, API externas o conectores. Por eso se combina con la revalidación de contenido y verificación posterior.

**No ejecutar antes del 10 de noviembre:** se necesita el paquete oficial, conciliación y plan del mes anterior. Uso previsto después de prepararlos:
```bash
git pull --ff-only
bash scripts/ubuntu_preflight_cierre.sh 2026-10
```

**Errores y recuperación:** ante cualquier fallo de revalidación o validación de archivos, el shell devuelve un código distinto de cero, libera el bloqueo al finalizar y **no habilita el archivado**. Un archivo `.lock` persistente no representa por sí mismo un proceso activo; `flock` se libera al cerrarse su descriptor. No se debe borrar manualmente el archivo de lock. En una futura carga interrumpida, habrá que revisar el respaldo íntegro y repetir reconciliación/read-back, sin sobrescribir a ciegas. Se documentará un mecanismo de recuperación específico antes de permitir escrituras del cierre.

**Estado:** bloqueo implementado en código; todavía requiere prueba de concurrencia sobre Ubuntu. No se ha ejecutado ni autorizado cargador de escritura o traslado. La cuenta de servicio tampoco puede impedir modificaciones de terceros mediante `flock`.

## Validación en Ubuntu — 21 de octubre de 2026

El usuario ejecutó las pruebas locales con `.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v`: **10 pruebas completadas, 10 OK, 0 fallas**. Después ejecutó dos adquisiciones concurrentes del archivo `logs/.mer_escritura_compartida.lock` mediante `flock -n`. La consola registró `BLOQUEO ADQUIRIDO` en el primer proceso y `CORRECTO: SEGUNDO PROCESO BLOQUEADO` para el segundo; ambos finalizaron sin intervención manual. **Esto prueba exclusivamente el comportamiento local del mecanismo flock**, no el cierre integral, ni una carga de Google Sheets, ni protección frente a editores externos.

Próximos controles: prueba de integración del lock en el ejecutor diario, cargador seguro con respaldo y verificación, y cierre supervisado de octubre a partir del 10 de noviembre. El cron mensual continúa deshabilitado.

## Novena etapa: núcleo de cargador remoto preparado, no habilitado

Se añadió `scripts/cargador_cierre_mer_v2.py`. Tiene una función interna desacoplada de la infraestructura para ensayar carga **solo de claves nuevas**, respaldo previo obligatorio, control de celdas, relectura antes de cada tabla y verificación posterior de las seis pestañas. Si aparece cualquier registro con la misma PK y valores diferentes, bloquea la operación **antes de escribir**, mientras no exista política de conciliación de campos. Los registros solo operativos se preservan.

La CLI no contiene opción `--aplicar`, no solicita credenciales ni crea conexiones Google: **no puede escribir remotamente cuando se ejecuta como programa**. Esta fase está intencionalmente sin activar para proteger la primera prueba supervisada del 10 de noviembre.

Pruebas con sustitutos de Google Sheets: `tests/test_cargador_cierre_mer_v2.py`. Comprueban que el respaldo anteceda a la carga y que diferencias existentes bloqueen cualquier escritura. Pendiente su ejecución en Ubuntu. La función interna fue desarrollada, pero todavía no se ha ensayado con hojas reales.

**Limitaciones que deben resolverse antes de activar:**
- Integrar la función con las implementaciones reales `respaldo_local`, `aplicar_tabla` y `worksheet_rows`, ejecutando siempre bajo `flock` compartido y revalidando huellas antes de empezar.
- Aprobar una política de actualización por campo para datos oficiales que difieren del operativo (el motor actualmente solo soporta altas).
- Prueba con dobles que simulen fallos a mitad de carga y reanudación idempotente; pruebas de cuota, tasa y recuperación de respaldos.
- Autorizar por separado escritura, auditoría final y traslado Drive; nunca tratar `CARGA_VERIFICADA` como permiso automático de archivado.
- Verificar la suma de celdas efectivamente asignadas después del crecimiento de Google Sheets; la predicción es preventiva y no sustituye inspección post-carga.

El ETL diario, el cron existente, las Google Sheets y el frontend no se modificaron en esta etapa.

## Décima etapa: interrupción simulada y reanudación idempotente

El núcleo `scripts/cargador_cierre_mer_v2.py` ahora captura fallos durante la aplicación de tablas, registra el estado `CARGA_INCOMPLETA_BLOQUEADA` mediante el evento `CARGA_INTERRUMPIDA` y **no emite `CARGA_VERIFICADA`**. Conserva `cierre_autorizado=false` y `traslado_autorizado=false`. Reanudar exige releer el destino, conservar claves ya escritas y repetir todas las comprobaciones y respaldo antes de comenzar.

Se añadió `tests/test_recuperacion_cargador_cierre.py` con dos casos simulados: (1) corte después de haber escrito parcialmente dos tablas, seguido de una reanudación que no duplica PK; (2) error de registro del respaldo que impide iniciar escrituras. El ensayo trabaja con **dobles de Sheets y SQLite en memoria**, sin acceso remoto.

Ejecutar localmente: `.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v`. Se esperan **14 pruebas**, sujeto a verificación desde Ubuntu. Todavía no está resuelto el rollback físico automático de escrituras parcialmente confirmadas por Google, la auditoría de modificaciones campo por campo ni la integración de permiso real de escritura. La CLI del cargador sigue sin opción de aplicar, y no se activa el cron mensual.

**Regla de recuperación:** una carga interrumpida no equivale a cierre; impedir todo traslado mientras falte read-back completo, respaldo y auditoría de seis tablas. Si hay diferencias inexplicadas, bloquear y revisar, no borrar ni reemplazar información automáticamente.

## Undécima etapa: auditoría referencial del paquete histórico

Se incorporó `scripts/auditar_referencias_cierre.py`. Examina exclusivamente el SQLite preparado de las seis entidades MER v2, contrastándolo contra los esquemas y conteos del importador. No accede a Google ni escribe. Los controles se dividen explícitamente en dos categorías:

- **Bloqueantes:** filas que contradicen cabeceras/PK MER v2, resultado asociado a una oferta existente de otro proceso, resultado histórico marcado como verificado jurídicamente sin la validación requerida, o vínculo sin código OC. El informe queda `AUDITORIA_BLOQUEADA` y termina con código distinto de cero.
- **Observaciones:** oferta o resultado sin proceso presente en el mismo corte, OC asociada a proceso de otro mes, proveedor no resuelto, vínculo cuya OC no figura en la fuente mensual, o divergencia de vínculo/proceso que requiere examinar otros meses. No bloquear de inmediato por estos casos, ya que los cortes oficiales pueden diferir temporalmente. **No equivale a aprobación automática**: corresponde evaluar y documentar su volumen y justificación.

El estado sin errores estructurales es `AUDITORIA_ESTRUCTURAL_SIN_ERRORES_CON_OBSERVACIONES`, pero conserva siempre `cierre_autorizado=false` y `traslado_autorizado=false`. La conciliación remota, carga final auditada y traslado requieren decisiones posteriores.

### Pruebas
```bash
.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v
```

Se añadieron dos escenarios de auditoría en `tests/test_auditar_referencias_cierre.py`: una OC fuera de corte se clasifica como observación y un resultado enlazado a una oferta de otro proceso bloquea el cierre. Se esperan **16 pruebas** en total, pendientes de ejecución en Ubuntu.

### Uso supervisado después de preparar los ZIP
```bash
.venv/bin/python scripts/auditar_referencias_cierre.py \
  --paquete "$HOME/.local/share/mercadopublico/cierres/2026-10/preparados"
```

Salida: `~/.local/share/mercadopublico/cierres/2026-10/auditoria_referencial.json`. El código no modifica datos ni activa el cron mensual.
