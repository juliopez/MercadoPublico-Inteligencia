# Cierre técnico y plan de validación — 22 de octubre de 2026

## Propósito
Conservar evidencia y estado exacto de la integración diaria Ubuntu → Google Sheets MER v2 → frontend V2 → GitHub Pages. Esta bitácora distingue instalación, simulación, escritura real, publicación y validación desatendida. Los horarios se expresan en America/Santiago.

## Evidencia reunida en Ubuntu (capturas del usuario)
- **21/10 16:00:** cron anterior ejecutado; `CARGA_VERIFICADA`, código 0. Lectura independiente del 22/10 comprobó 1.856 Procesos y 99.811 OC. En Procesos, 1.558 previos y 298 nuevas claves; discrepancia inicial de lectura resuelta.
- **22/10:** ZIP OC de octubre, 302.727 filas; extracción de 8.723 pares COT–OC desde `Descripcion/Obervaciones`.
- Consulta multimes de MER junio–octubre: 861 pares ya existentes, 5.339 sin COT presente, 2.523 elegibles con COT registrada y 8 OC ambiguas excluidas.
- Aplicación supervisada: 2.523 insertados y verificados en `MER_2026_10_OPERATIVO.VinculosCOT_OC`; estado `CONCILIACION_VERIFICADA` y respaldo local previo. Nueva simulación: 3.384 existentes y **0** pendientes, corroborando idempotencia.
- Cron Ubuntu reemplazado localmente: entrada `0 * * * * /bin/bash ".../scripts/ubuntu_cron_integrado.sh" --cron`. Filtro interno lunes a viernes 16:00. Se conservó respaldo de crontab y scripts anteriores.
- Exportadores en modo **simulación**: 1.856 Procesos, 99.811 OC. Exportación documental: 2.524 vínculos documentales encontrados en MER, 2.523 nuevos frente al JSON público preexistente, total proyectado 3.935. No equivalen a publicación.
- Prueba correctiva: se reparó la concatenación de dos comandos en `ubuntu_publicar_v2_post_etl.sh`. Se repitió simulación y terminó sin error.

## Código integrado (publicado, todavía sin ejecución automática integral verificada)
1. `scripts/ubuntu_cron_integrado.sh`: ETL original dos ZIP, conciliación incremental, invocación del publicador.
2. `scripts/etl_conciliacion_cot_oc.py`: fuente descriptiva OC, contraste multimes, deduplicación y respaldo.
3. `scripts/descargar_oc_incremental.py`: caché y verificación del ZIP OC.
4. `scripts/exportar_mer_operativo_v2.py`: Procesos y OC a fragmentos JSON públicos.
5. `scripts/exportar_vinculos_documentales_v2.py`: relaciones documentales, conservando las previamente publicadas y excluyendo ambigüedades.
6. `scripts/ubuntu_publicar_v2_post_etl.sh`: publicación vía Git **solo** tras sincronización exitosa y con autenticación adecuada.
7. `.github/workflows/publicacion-v2-post-etl.yml`: horario lógico 17:00 de Santiago, genera derivados y verifica conteos antes de commit.

### Cobertura y decisiones
- **Cron diario solo dos fuentes oficiales:** licitaciones y órdenes de compra. Compra Ágil NO dispone de ZIP diario garantizado; no descargarlo ni vaciar/modificar Ofertas/Resultados por ausencia de fuente.
- Históricos junio–septiembre inmutables. No reprocesar ni duplicar los 240.649 pares estructurados y 1.411 relaciones documentales verificadas previamente.
- El MER operativo conserva seis tablas. La publicación V2 usa fragmentos para Procesos/OC, vínculos documentales y derivados públicos; las tablas Ofertas y Resultados continúan sin alimentación diaria.
- **Tarea 5 — API Compra Ágil**: pendiente, separada del cron actual y de su puesta en marcha.
- No publicar credenciales, RUT privados, descripciones documentales extensas, ZIP históricos, respaldos ni bitácoras de Ubuntu.
- Mantener fuente, fecha y certeza de vínculos; la referencia documental NO prueba pago o adjudicación.

## Validación tras las 17:00 del 22/10 — palabra de inicio «valida»
1. **Ubuntu:** consultar `salida_operativa/estado_sincronizacion.json`, `salida_operativa/estado_conciliacion.json`, `logs/orquestador_integrado_*.log`; contrastar fecha, éxito, cambios y errores. Revisión local si el asistente no puede acceder.
2. **Google Sheets:** verificar conteos y la persistencia de nuevos vínculos sin alterar otras tablas ni las últimas marcas de éxito.
3. **GitHub:** confirmar commit de actualización del catálogo, partes de Procesos/OC y `vinculos-oc-verificados.json` del día; contrastar conteos, no solo hora de commit.
4. **Actions:** comprobar ejecución efectiva del workflow posterior, generación y conteo de `busqueda/`, `perfiles/`, `analitica/`, `indices/` y `relaciones-procesos/`; horarios UTC pueden cambiar por horario de verano.
5. **Pages y V2:** verificar recurso servido (no solo en rama `main`), contadores y códigos representativos, búsqueda transversal, «Ver detalle» y vínculos OC. Informar estados: aprobado, fallo concreto o pendiente por evidencia.
6. **Reintentos y recuperación:** comprobar que una falla de push/Actions no altere datos verificados en Sheets y que no se vuelva a insertar una PK existente. No ejecutar nuevas cargas históricas para auditar.

## Advertencias de cierre
- **No se acredita aún** una ejecución completa desatendida de Ubuntu 16:00 → GitHub 17:00 → Pages.
- El éxito de `git pull`, `bash -n` o una simulación **no acredita** push desatendido, despliegue ni validación visual.
- GitHub Actions programado se activa solo al detectarse exportación pública reciente. Si no ocurre, identificar si falló la carga, publicación Git o generación de derivados.
- El documento `PLAN_MEJORAS_CRON_1600_2026-10-21.md` es histórico: describía una propuesta anterior a la instalación del 22/10. No usarlo como estado vigente.

## Referencias
- `docs/CRON_INTEGRADO_UBUNTU_2026-10-22.md`
- `docs/PUBLICACION_MER_V2_POST_ETL_2026-10-22.md`
- `docs/ENRIQUECIMIENTO_OC_DESCRIPCIONES_2026-10-21.md`
- `docs/AUDITORIA_DIFERENCIAL_COT_OC_2026-10-21.md`

## Incidencia real del cron 16:00, observada a las 16:13 de Santiago
- El ETL actualizó MER operativo en Google Sheets (captura del registro local): Procesos 2.094, ÓrdenesCompra 108.269 en exportación; los conteos de carga incluyeron 8.458 OC nuevas, 8.426 modificadas, 814 proveedores nuevos.
- El publicador de Ubuntu falló en `scripts/exportar_mer_operativo_v2.py`, en `os.replace` desde `/tmp/export_mer_v2_*/procesos/2026-10/0003.json` hasta el repositorio, con `OSError: [Errno 18] Invalid cross-device link` (EXDEV). Mensaje local: `PUBLICACION_V2_FALLIDA`.
- Se corrigió la exportación mediante copia a archivo temporal **en el mismo directorio de destino** y reemplazo atómico local; commit `5f06d6aa`. **La corrección aún no se ha ejecutado ni verificado en Ubuntu**, por lo que no implica publicación automática exitosa hoy.
- La orquestación de las **17:00 se ejecuta en GitHub Actions**, no en Ubuntu. Su workflow `publicacion-v2-post-etl.yml` verifica un commit fresco en `catalogo-publico.json` o `vinculos-oc-verificados.json` posterior a las 16:00. Como la publicación Ubuntu falló antes de generar ese commit, puede concluir en modo `SIN_ORIGEN_FRESCO` sin actualizar los derivados; no darla por fallida ni por exitosa hasta examinar su ejecución y fuente.
- No volver a ejecutar el ETL de carga histórica ni alterar las hojas por este problema de publicación; cualquier reparación debe ser **solo de exportación** desde MER ya actualizado, con comprobaciones de integridad y sin escritura a Sheets. Mantener separados el publicador del MER y el workflow de derivados/Pages.

## Bitácora de control y traspaso a revisión de las 17:00 — 22/10/2026

### Línea de tiempo y nivel de evidencia
| Hora Chile | Evento | Evidencia y conclusión |
|---|---|---|
| 16:00:01 | Activación del cron integrado de Ubuntu | Archivo local `logs/orquestador_integrado_20261022_160001.log` mostrado por el usuario |
| 16:08 | Inspección del estado de carga | El estado de sincronización registra 8.458 OC nuevas, 8.426 modificadas y 90.832 sin cambios; 814 proveedores nuevos, 0 modificados y 19.292 sin cambios. No confirma por sí solo la conciliación |
| 16:13 | Inspección del log del orquestador | Exportación de MER operativo alcanzó 2.094 Procesos y 108.269 OC, seguida de `PUBLICACION_V2_FALLIDA` y `OSError [Errno 18] Invalid cross-device link` al trasladar fragmentos desde `/tmp` |
| Posterior a 16:13 | Corrección técnica publicada en GitHub | `scripts/exportar_mer_operativo_v2.py`, commit `5f06d6aa`: copia a temporal del mismo destino y `os.replace` local atómico; **no aplicada ni comprobada todavía en Ubuntu** |
| Posterior a 16:13 | Actualización de esta bitácora | Commit anterior `07396811` y registro del presente traspaso; no constituye ejecución de ETL |
| 17:00 (programado) | `.github/workflows/publicacion-v2-post-etl.yml` | Revisión pendiente; el disparador programado y sus resultados deberán confirmarse en GitHub Actions |

### Semántica operacional
1. **16:00, Ubuntu:** ETL de dos fuentes, persistencia MER en Sheets, conciliación COT–OC y exportación/publicación de fragmentos públicos. La prueba disponible confirma carga y error de publicación, pero no acredita por sí sola cierre correcto de todos los pasos.
2. **17:00, GitHub Actions:** workflow independiente, encargado de construir índices, perfiles y analítica **a partir de un catálogo y fragmentos publicados recientemente**. No descarga ZIP ni actualiza Sheets.
3. **Pages:** despliegue público independiente del éxito del workflow de derivados; validar siempre commit y contenido realmente servido.
4. **Compra Ágil / tarea 5:** sin API diaria en este ciclo; permanece en pausa por decisión expresa.

### Incidencia técnica y efecto esperado
El fallo `EXDEV` ocurrió **después** de operaciones de carga del MER y **antes** de generar el commit público esperado. En consecuencia, a las 17:00 GitHub Actions podría ejecutarse correctamente, pero omitir la generación por ausencia de una publicación fresca. Diferenciar **ejecución del workflow** de **actualización efectiva de datos**.

Los archivos locales parcialmente generados por una exportación interrumpida no se deben asumir coherentes. La recuperación debe regenerar íntegramente los fragmentos del mes operativo desde Sheets, comprobar catálogo, conteos y referencias de partes y solo entonces confirmar la publicación. No volver a ejecutar la carga del ETL ni repetir la escritura de Sheets para corregir este incidente.

### Protocolo acordado
El usuario regresará después de las 17:00 con el mensaje **«validar»**. En esa oportunidad:
- Consultar ejecución y logs del workflow de las 17:00, incluyendo paso `Comprobar exportacion nueva y hora de Santiago` y resultado `ready`.
- Verificar si existe un commit de **datos operativos** posterior a las 16:00 y si sus fragmentos y catálogo son coherentes. No confundir commits de código o documentación con exportación.
- Comprobar los 2.094 Procesos y 108.269 OC reportados en la simulación de exportación únicamente como referencia a contrastar con la publicación final.
- Comprobar vínculos documentales COT–OC, derivados, enlaces, índices y Pages; clasificar cada componente en **verificado**, **fallido** o **pendiente por falta de evidencia**.
- Si falta el origen público, proponer **solo recuperación de exportación**, con la corrección GitHub ya registrada, sin intervenir los históricos ni Sheets.

**Estado al cierre de esta bitácora:** ejecución Ubuntu con actualización de datos observada, publicación pública fallida, corrección documentada pero no instalada en Ubuntu, GitHub Actions 17:00 y Pages posteriores aún pendientes de comprobación.

## Auditoría 17:34 Chile — estado post-16/17 (22/10/2026)
- Con evidencia de las capturas locales de las 16:08 y 16:13, el ETL Ubuntu cargó los datos MER; exportador falló por EXDEV antes del commit público. Conciliación COT–OC aún no confirmada en el log.
- Inspección GitHub Actions a las 17:34: ningún run de `Publicacion V2 posterior al ETL Ubuntu` identificado entre las ejecuciones actuales ni entre las recientes de tipo `schedule`. No equiparar ausencia observada a deshabilitación demostrada: Actions programadas pueden presentar retrasos; verificar el workflow y su historial específico.
- `frontend-v2/data/catalogo-publico.json` continúa con `fecha_publicacion=2026-10-21T17:40:40.753435+00:00` y octubre `procesos=1558`, `ordenescompra=91070`, mientras que el exportador Ubuntu reportó 2094 y 108269. Nuevos registros no están publicados.
- El workflow de analítica genérica V2 (lanzado por cambios del frontend) tuvo ejecuciones exitosas previas. No implica regeneración de derivados del cron diario.
- Incidencia pendiente de recuperación controlada: instalar el arreglo EXDEV, revisar estado Git local tras exportación parcial, **no repetir carga Sheets**, exportar solo MER desde estado ya persistido y verificar commit fresco, luego reconstruir los derivados en GitHub. No registrar éxito hasta comprobarlo.

## Cierre de incidencia monetaria y endurecimiento de automatización — 22/10, 18:49
**Validación visible del frontend:** el usuario mostró octubre con 2.094 procesos, ranking monetario y dona de concentración del presupuesto. Github JSON de octubre comprobado: 794 registros con monto y presupuesto agregado CLP 18.441.856.682. Pages finalizó con éxito tras el enlace al workflow de derivados.

**Mejoras para el 23/10 incorporadas en repositorio:**
1. El importador de licitaciones selecciona `MontoEstimado` únicamente si `CodigoMoneda=CLP`, `Estimacion=1` y `VisibilidadMonto=1`; el rescatador monetario sigue siendo herramienta de reparación controlada, **no un segundo ETL diario**.
2. `scripts/ubuntu_cron_integrado.sh`: prueba preoperativa del helper CLP y compilación de importador, conciliación y exportadores antes de comenzar a escribir Sheets. Si el código local es antiguo, aborta antes de cargar datos. No cambia las 16:00.
3. `.github/workflows/publicacion-v2-post-etl.yml`: comprobaciones programadas a los minutos 00/15/30/45 en las horas UTC correspondientes a las 17:00 de Santiago (verano e invierno). La guarda de `America/Santiago` impide generación fuera de 17:00, y `git diff --cached --quiet` evita nuevos commits sin cambios. El reintento del mismo día permite que una publicación atrasada sea recogida sin ejecutar ETL adicional. Se valida conteo monetario en rango, monto no negativo y piso de 794 procesos con presupuesto CLP para octubre (regresión de incidente).
4. `.github/workflows/preview-frontend-v2.yml`: recibe `workflow_run` exitoso de derivados y despliega Pages, sin depender de `push` ejecutado con `GITHUB_TOKEN`.
5. Publicador Ubuntu sigue usando staging temporal en el mismo filesystem para evitar `EXDEV`, mantiene exportaciones sin escrituras Sheets y publica solo fragmentos, catálogo y vínculos de mes operativo.

**Pendiente que impide certificar automatización futura:** instalar commits en Ubuntu con `git pull --ff-only` y ejecutar `bash scripts/ubuntu_cron_integrado.sh --verificar` (sin ETL); confirmar que los workflows modificados validan en Actions. La ejecución desatendida del viernes 23/10 aún no ha ocurrido. No declarar éxito automático de mañana por la recuperación manual de hoy.

**Prueba local no destructiva:**
```bash
cd "$HOME/Julio Lopez/chilecompra/MercadoPublico-Inteligencia" || exit 1
git pull --ff-only origin main
bash scripts/ubuntu_cron_integrado.sh --verificar
crontab -l | grep 'ubuntu_cron_integrado.sh'
```

## Cierre integral de frontend V2 — jornada del 22/10/2026

**Confirmaciones del usuario:** las ayudas metodológicas, el menú superior sticky, la navegación y la nueva visualización circular de participación empresarial recibieron aprobación visual y funcional expresa. Los datos y las definiciones se mantuvieron separados de las afirmaciones contractuales.

### Cambios entregados
1. **Usabilidad global:** ayudas contextuales centralizadas (`frontend-v2/js/ayudas-contextuales.js`), con activación mediante teclado/clic y CSS adaptable; navegación principal sticky y compensación de anclajes. Se ajustaron contrastes, jerarquía y organización de consultas y gráficos.
2. **Evolución mensual:** tarjetas simultáneas de montos registrados, concentración monetaria por organismo y actividad; advertencias de meses parciales, unidades CLP y variaciones. El último ajuste aprobado elimina `analitica-vista` y el resaltado arbitrario de tarjetas; **permanece el selector funcional «Comparar con»**. Cambios `4f05616d`, `c3aa3681`, `b7383731`.
3. **Perfil de participantes:** métricas por participación, efectividad y resultados económicos; nuevos registros de selección histórica, procesos seleccionados únicos y suma de ofertas seleccionadas. Sin interpretar selección como contrato ni pago. Monto adjudicado y procesos ganados contractualmente continúan pendientes de acreditación.
4. **Deduplicación y tasas:** se agregaron códigos de participación y selección a los índices JSON mensuales; la tasa es selección registrada sobre procesos únicos ofertados, no adjudicación. Caso MULTITODO SPA: 845 ofertas, 834 procesos únicos (222 jun, 202 jul, 208 ago, 202 sep; 0 duplicados intermes), 172 selecciones únicas, 20,6 % y $140.085.411 en ofertas seleccionadas.
5. **Gráfico empresarial:** reemplazo de barras por dona SVG dinámica basada en recuentos públicos; leyenda mes/registro/porcentaje, total central, explicación clara y botones «Examinar período». La distribución 224/205/213/203/0 fue validada visualmente por el usuario.
6. **Datos/operación:** incidencia presupuestaria de octubre subsanada. 794 procesos con monto CLP, 2.094 procesos publicados, agregación $18.441.856.682, perfiles y analítica regenerados; Pages comprobado por capturas después de ajustes.
7. **GitHub Actions:** corrección de propagación derivados→Pages mediante `workflow_run`; conflicto al publicar participación mes por mes resuelto mediante regeneración del conjunto y un commit, con gestión de concurrencia. Las ejecuciones canceladas por pushes cercanos no implican fallo del ETL. Cron Ubuntu 16:00 y workflow principal 17:00 preservados.

### Alcance y límites de cierre
No se reescribieron históricos ni se alteró la BBDD Google Sheets para implementar UX. El cron local fue instalado y comprobado con `--verificar`, pero **la ejecución desatendida del viernes 23/10 sigue pendiente de auditoría real**. La tarea 5 de API Compra Ágil se abordará después de esa auditoría. Se requiere verificar éxito del último despliegue Pages del ajuste de perspectiva; los commits en GitHub no demuestran por sí solos que ya estén visibles.

### Auditoría del 23/10
Revisar la secuencia cron Ubuntu 16:00 → Sheets y conciliación → exportación catalogada y vínculos → GitHub Actions cerca de 17:00 Santiago → índices/analítica y validación → Pages público. Confirmar logs, idempotencia, conteos y estado de los workflows sin repetir manualmente el ETL.
