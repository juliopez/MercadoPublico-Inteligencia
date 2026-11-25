# Conciliación cronológica matinal del MER — 09:00

## Actualización vigente — 25/11/2026, recuperación de la conciliación 09:00

Incidente #91: publicador rechazó el último período exportado (octubre histórico). Corrección autorizada `b25ee1246` en publicacion-v2-post-etl.yml; reconoce conciliación y regenera derivados de períodos afectados, manteniendo guardas para otros orígenes. Commit de recuperación `2a3f7b4ae` a las 09:33:06 acredita publicación de derivados junio–noviembre. Captura del operador confirma frontend con 26.838 procesos de noviembre y fecha de publicación 25/11 09:12; coincide con catálogo, analítica y dimensión de Sheets menos encabezado. Incidente recuperado; siguiente conciliación natural debe acreditar funcionamiento sin intervención. No repetir conciliación ni reparación. La comparación de snapshots nocturno `bce75616b` y matinal `844dd7b7f` muestra noviembre 27.232 → 26.838 (-394), históricos +134 (junio +2, julio +2, agosto +5, septiembre +21, octubre +104), total -260. El conciliador conserva PK históricas existentes y retira del operativo solo tras verificar presencia en destino; los 260 son compatibles con deduplicación, no confirmados individualmente. No afirmar pérdida ni ausencia de pérdida sin cotejo por PK o evidencia local. Referencia: [runbook 09:00](CONCILIACION_CRONOLOGICA_0900.md). La mitigación de artefacto Pages del 24/11 (`a06fbfde`) es independiente; sin log de espera/reintentos no certificar su eficacia frente a nueva demora. P2/P4 de auditoría cerrados; P1 favorable con limitaciones locales y P3 nocturno/fin de semana en seguimiento. No confundir códigos de auditoría con IDs de inventario.


**Alta documental:** 2026-11-09, hora de Chile. **Estado:** implementada en `main`, cron instalado en Ubuntu según captura de `crontab -l` aportada por el responsable; ejecuciones y recuperación acreditadas; consultar actualizaciones de vigencia.

## Objetivo y alcance

Revisar el MER **operativo** vigente y trasladar registros que, por su **fecha oficial propia**, correspondan a otro período MER disponible. Es un proceso distinto de la **conciliación oficial de mes vencido P4** (ZIP y cierre histórico), que permanece protegida y sin cambios. Tampoco sustituye el cron 16:00, la API de licitaciones 16:15 ni Compra Ágil 22:05.

## Disparador y archivos

- **Ubuntu crontab:** `0 9 * * 1-5` (lunes a viernes, 09:00, hora local validada frente a `America/Santiago`).
- **Etiqueta:** `# MER_CONCILIACION_0900`.
- **Instalación idempotente:** `scripts/instalar_cron_conciliacion_0900.sh`.
- **Orquestador:** `scripts/ubuntu_conciliar_mer_0900.sh`.
- **Motor:** `scripts/conciliar_mer_cronologico.py`.
- **Log:** `logs/conciliacion_mer_0900.log`.
- **Informe local:** `salida_operativa/conciliacion_cronologica.json`.
- **Publicación:** `scripts/exportar_mer_operativo_v2.py` con autorización explícita `MER_CONCILIACION_PERIODOS=1`; commit/push de catálogo y fragmentos afectados.

## Reglas de clasificación aprobadas

| Hoja MER | Fecha rectora | Conducta |
|---|---|---|
| `Procesos` (licitaciones y Compra Ágil) | `fecha_publicacion` | Clasificar por mes oficial de publicación |
| `OrdenesCompra` | `fecha_creacion` | Clasificar por mes de creación de la OC, aunque el proceso relacionado pertenezca a otro mes |
| `Ofertas` | `fecha_oferta` | Clasificar por fecha propia de oferta |
| `Resultados` | `fecha_resultado` | Clasificar por fecha propia del resultado |
| `Proveedores` | Sin fecha propia | No trasladar automáticamente |
| `VinculosCOT_OC` | Sin fecha propia | No trasladar automáticamente |

Fechas ausentes, inválidas o períodos sin MER histórico configurado: **no se trasladan**; se contabilizan como pendientes. Las relaciones entre entidades se conservan por sus identificadores y pueden cruzar períodos.

## Secuencia implementada

1. Verificar credenciales, entorno, Git limpio y obtener `main` actualizado.
2. Adquirir lock propio `.conciliacion_mer_0900.lock` y lock de escritura compartido `.mer_escritura_compartida.lock`.
3. Leer las cuatro hojas fechadas del MER operativo, determinar destino por fecha propia y elaborar informe.
4. Si hay movimientos, abrir MER históricos configurados y respaldar íntegramente las seis hojas del operativo y de cada destino antes de escribir.
5. Insertar PK faltantes en destino **sin sobrescribir registros históricos existentes**; comprobar PK y contenido de nuevas filas mediante lectura posterior.
6. Retirar del origen únicamente filas verificadas en destino, en orden descendente; comprobar que ya no están en origen.
7. Exportar los períodos afectados y el operativo a fragmentos públicos V2; commit/push para activar la cadena de índices y publicación.

## Limitaciones y riesgos que se deben auditar

- La eliminación en Google Sheets se realiza por filas y puede ser lenta; ante interrupción, el proceso debe reanudarse con las PK restantes, verificando destino. **No asumir atomicidad entre dos hojas.**
- En una PK ya existente en histórico, se conserva el registro histórico, incluso si el operativo posee información más completa; **no existe aún fusión de campos**.
- `Proveedores` y `VinculosCOT_OC` permanecen en el operativo; no hay traslado automático de estas entidades ni exportación pública específica de ellas.
- El proceso puede mover registros a MER históricos, por lo que constituye una **excepción autorizada por el responsable** a la inmutabilidad habitual de históricos. No debe confundirse con una conciliación oficial del día 10 hábil.
- La exportación posterior exige que la conciliación llegue al estado `CONCILIACION_VERIFICADA`; la regeneración final de índices y GitHub Pages requiere auditoría aparte.
- Si se interrumpe después de escribir Sheets pero antes de publicar, debe contrastarse la consistencia entre MER y catálogo.
- Primera ejecución **no validada** al redactar este documento: no afirmar cantidades trasladadas, publicación ni éxito de cron hasta revisar el log y los MER reales.

## Auditoría de primera ejecución — martes 10/11/2026

Consultar en Ubuntu:

```bash
crontab -l | grep MER_CONCILIACION_0900
tail -n 100 logs/conciliacion_mer_0900.log
cat salida_operativa/conciliacion_cronologica.json
```

Contrastar: inicio cercano a 09:00; tabla/mes y PK transferidas; fechas inválidas; respaldo de origen y destinos; relectura y retiro; errores 429/5xx; locks; commit/push; índices derivados y catálogo efectivamente servido por Pages. Si el equipo está apagado o suspendido a las 09:00, el cron local no ejecuta retroactivamente.

## Referencias de implementación

- Motor: commits `ecd0cc9` y corrección de fechas `2a357e1`.
- Exportación histórica habilitada de forma explícita: `5d18a8a`.
- Orquestador: `350bac6`.
- Instalador: `818ff63`.
- Instalación en Ubuntu: captura de `crontab -l | grep MER_CONCILIACION_0900` del 09/11/2026.

## Incidente 17/11/2026 y aislamiento instalado (recuperación acreditada)

El cron se disparó a las 09:00:01, pero el log terminó con `GIT_NO_LIMPIO`; el archivo rastreado `scripts/asistente_ia/backend/adaptador-worker.mjs` tenía cambios locales. No se acreditó conciliación del 17/11. No descartar esos cambios.

Corrección propuesta en PR: el cron llama a `scripts/ubuntu_conciliar_mer_0900_aislado.sh`, que utiliza un clon dedicado en `~/.local/share/mercadopublico/conciliacion-runtime` y el Python virtual del proyecto original, sin alterar su árbol de desarrollo. El motor conserva las validaciones y usa `MER_LOCK_DIR` para compartir los mismos locks con el entorno original. El log del cron permanece en el directorio original, pero el informe `salida_operativa/conciliacion_cronologica.json` queda en el runtime aislado. Las credenciales siguen en el perfil Ubuntu.

**Activación:** una vez fusionado el PR, ejecutar el instalador desde una copia limpia del código o actualizar solamente los scripts aprobados en el equipo sin descartar modificaciones locales. Verificar `crontab -l` antes de iniciar una recuperación manual; no permitir dos conciliaciones simultáneas. Ejecutar el wrapper manualmente una vez para recuperar 17/11 y revisar el log, el informe del runtime, los cambios MER y la publicación. La aprobación del código en GitHub no instala ni ejecuta por sí sola el cron de Ubuntu.


### Cierre verificado el 17/11/2026 (evidencia Ubuntu proporcionada)

- PR #22 fusionado a `main` (commit `1fdd4ffaa580dbbf4cf22a6f45ec859ebc6cd6be`): wrapper aislado `scripts/ubuntu_conciliar_mer_0900_aislado.sh`, `MER_LOCK_DIR` compartido y ajuste del instalador cron.
- En Ubuntu se actualizó la entrada de `crontab` para invocar el wrapper aislado, se preparó el runtime independiente y se ejecutó manualmente la conciliación pendiente.
- El registro local mostró `CONCILIACION_PUBLICADA 2026-11-17T10:21:43-03:00`; la ejecución publicó exportaciones e índices en `main`. Esta evidencia acredita finalización y push; la comprobación independiente de Pages debe auditarse por separado.
- Para recuperar el repositorio de desarrollo, se guardó la modificación local de `scripts/asistente_ia/backend/adaptador-worker.mjs` en `stash@{0}` (mensaje `respaldo-adaptador-worker-2026-11-17`), se respaldó fuera del árbol la copia no rastreada del wrapper y se hizo `git pull --ff-only origin main`.
- La versión de `main` ya tenía `maxOutputTokens: 2048`; por ello **no se aplicó el stash**. `git status --porcelain --untracked-files=no` no devolvió modificaciones rastreadas. Permanecen archivos locales no rastreados (logs, salida_operativa y scripts auxiliares), **no eliminados**.
- Estado: causa `GIT_NO_LIMPIO` mitigada mediante aislamiento; recuperación manual completada; próximo cron autónomo de 09:00 **pendiente de observación**, sin prometer éxito frente a fallas ajenas al bloqueo corregido.

> Nota de vigencia: las instrucciones anteriores de «activación pendiente» describen el estado previo a esta recuperación y no deben utilizarse como diagnóstico actual.


## Incidente 25/11/2026 — bloqueo de derivados tras conciliación multimes

Evidencia: MER operativo modificado 09:08 Chile; exportación `844dd7b7f` 09:12; participación `1e787328f` 09:14. Catálogo de main con ultima_exportacion.periodo=2026-10, aunque el operativo es noviembre. El operador aportó captura del workflow Publicacion V2 posterior al ETL Ubuntu #91, paso Comprobar exportacion nueva y hora de Santiago: BLOQUEO: período exportado ajeno al operativo o cierre excepcional (exit 1); los pasos de derivados quedaron omitidos. Los seis conteos de procesos del catálogo y analítica coinciden; noviembre 26.838, coincidente con dimensión de Sheets menos encabezado. No repetir la conciliación.

Corrección autorizada: [b25ee1246](https://github.com/juliopez/MercadoPublico-Inteligencia/commit/b25ee12461b0836e31098ffcc8124e9e7625bdae), exclusivamente publicacion-v2-post-etl.yml. Identifica el último commit que modifica catálogo por asunto exacto e identidad de autor Git configurada en el orquestador (identificación operativa, no autenticación criptográfica); obtiene períodos afectados por fragmentos/analítica del commit, exige que estén catalogados, regenera y valida derivados de cada uno. Conserva la restricción para los demás orígenes y la ventana schedule. El cambio del YAML activa su disparador push. Se verificó el contenido en main; la ejecución y Pages fueron corroborados posteriormente; ver actualización de recuperación; no modificar MER, ETL, API ni cron. La mitigación de disponibilidad de artefacto Pages del 24/11 es independiente.
