# Auditoría e inventario preliminar de GitHub Actions — 23/11/2026

## Alcance y criterio de evidencia

Auditoría **parcial**, independiente del entorno Ubuntu. Se revisaron archivos de workflows y documentación del repositorio, además de los jobs y logs de ejecuciones identificadas. No fue posible enumerar exhaustivamente todos los YAML habilitados ni todas las ejecuciones recientes mediante la conexión disponible. **No interpretar este inventario como censo completo de Actions**. No se dispararon workflows ni se alteraron datos durante esta auditoría.

Distinguir: (1) workflow documentado; (2) YAML verificado en `main`; (3) ejecución verificada; (4) registros incorporados; (5) exportación y Pages verificados. `success` no acredita automáticamente (4) ni (5).

## Inventario documental de 28 workflows

Fuente: `docs/GITHUB_ACTIONS_MANTENIMIENTO.md` y dos workflows de recuperación revisados. Los siguientes 26 nombres son **referencias documentales**, no confirmación individual de existencia/habilitación actual:

- **Publicación/operación (7):** `front-pages.yml`, `publicar-frontend-v2.yml`, `preview-frontend-v2.yml`, `publicar-sheets-pages.yml`, `publicar-solo-sheets.yml`, `observatorio-unico.yml`, `etl-loba-puntual.yml`.
- **Datos/índices V2 (7):** `generar-analitica-v2.yml`, `publicar-relaciones-procesos-v2.yml`, `indexar-relaciones-v2.yml`, `publicar-perfiles-v2.yml`, `publicar-autocompletado-v2.yml`, `publicar-sugerencias-global-v2.yml`, `ampliar-busqueda-v2.yml`.
- **Validación/integración (4):** `validar-analitica-historicos-v2.yml`, `validar-ux-integral-v2.yml`, `validar-busqueda-v2.yml`, `validacion-mer.yml`.
- **Pruebas específicas (8):** `validar-ajustes-landing-v2.yml`, `validar-buscador-global-v2.yml`, `validar-combinaciones-busqueda-v2.yml`, `validar-comparador-v2.yml`, `validar-favoritos-csv-v2.yml`, `validar-paquete-analitico-v2.yml`, `validar-perfiles-v2.yml`, `validar-presentacion-detalle-v2.yml`.
- **Recuperación de fin de semana (2):** `compra-agil-recuperacion-sabado.yml`, `compra-agil-recuperacion-domingo.yml`.

**YAML examinados directamente:** `preview-frontend-v2.yml` (workflow_dispatch, workflow_run y push filtrado; Pages), `publicar-frontend-v2.yml` (exportación por entidad/mes, workflow_dispatch y push filtrado), ambos recuperadores de fin de semana (schedule UTC doble por horario de Chile, workflow_dispatch, concurrencia `mer-api-actions-unica`, timeout 540 min). La búsqueda de `publicar-sheets-pages.yml` por ruta exacta no devolvió archivo; no concluir eliminación definitiva ni inactividad sin censo.

## Ejecuciones verificadas e incidentes

| Ejecución | Identidad | Evidencia |
|---|---|---|
| `44977382632` | Workflow de sábado, ejecución tardía 21/11 23:43 Chile | Job `success` pero selector `SIN_AUTORIZACION_O_PENDIENTES`; recuperación y publicación omitidas |
| `44983026915` | Segundo disparo del workflow de sábado, 22/11 00:59 Chile | Mismo resultado: 0 recuperación; no corresponde a workflow dominical |
| `45105256358` | Workflow dominical; inicio 23/11 00:19 Chile | Selector eligió 01/11; 64 consultas, 64 procesos, 419 ofertas, 43 resultados, 0 errores finales, un 429 recuperado; checkpoint de 01/11 completo; exportación y Pages verificadas |

En la ejecución dominical, el salto a 02/11 produjo `KeyError: '2026-11-02'` al consultar una jornada sin checkpoint. Los pasos posteriores de exportación y Pages continuaron y verificaron 22.781 procesos, 117.618 OC, 465 ofertas, 43 resultados. Se corrigió el acceso al estado faltante en `main`: sábado `132babdafde83cf81f38f2b00867ff7e8adb52d6`, domingo `84da57fcd3ca69be2852cc7b40d7f79d6b58dd25`. **La corrección todavía requiere validación mediante nueva ejecución real**.

La conciliación cronológica local de las 09:00 del 23/11 redistribuyó registros y publicó cerca de las 09:12, según capturas de Ubuntu aportadas durante la sesión; esa evidencia pertenece a la futura auditoría Ubuntu. El catálogo posterior de `main` registró 22.354 procesos, 103.092 OC, 465 ofertas y 43 resultados. La diferencia de procesos (427) coincide con el traslado informado por la conciliación. La diferencia de OC (14.526) coincide con la suma de traslados de la conciliación: 12.741 a octubre, 1.172 a septiembre, 335 a agosto, 146 a junio y 132 a julio. No hay diferencia residual de 1.785 OC.

## Proceso de las 10:15: sin identificar

**No se verificó un workflow de GitHub Actions programado para las 10:15.** No inferir ejecución, éxito, ausencia ni ubicación a partir del servicio Ubuntu `mercadopublico-conciliacion.service` ejecutado a las 08:43: son evidencias distintas. El inventario documental contiene una referencia histórica a `mercadopublico-conciliacion.timer` (10:00) que puede estar desactualizada; contrastar con Actions y configuración real antes de resolver la discrepancia. No confundir 09:15 con 10:15.

## Pendientes para cierre de auditoría GitHub

1. Enumerar todos los archivos en `.github/workflows/` y todos los workflows registrados (activos, deshabilitados y manuales); cruzar nombres, IDs, disparadores, UTC/Chile, concurrencia, permisos y secretos.
2. Obtener últimas ejecuciones por workflow, conclusión de cada job, pasos omitidos, volumen de datos, errores y checkpoints.
3. Identificar o descartar con evidencia el workflow atribuido a las 10:15 y revisar sus últimas ejecuciones.
4. Reconciliar exportaciones, catálogo de `main` y Pages tras conciliación 09:00; la diferencia de 14.526 OC queda explicada por los traslados del log de conciliación: 12.741 a octubre, 1.172 a septiembre, 335 a agosto, 146 a junio y 132 a julio (total 14.526).
5. Validar el arreglo `KeyError` de fin de semana en la próxima ejecución real.
6. Solo después, contrastar con cron/systemd instalado en Ubuntu y elaborar inventario consolidado.

**Política:** auditoría de solo lectura; no eliminar, reprogramar ni ejecutar procesos productivos sin autorización.

## Verificación posterior a aprobación (23/11)

Se reabrieron los YAML vigentes `compra-agil-recuperacion-sabado.yml` y `compra-agil-recuperacion-domingo.yml`. Ambos ya contienen en el chequeo de enfriamiento posterior al cambio de jornada: `json.load(...).get('jornadas_actions',{}).get(os.environ['MER_API_FECHA_OBJETIVO'],{})` (línea 131). Esta es la corrección del `KeyError: '2026-11-02'` que se observó en el log del run `45105256358`; no es necesario duplicarla. La consulta inicial del estado de la jornada actual en la línea 106 se ejecuta **después** de `mer_api_recuperacion_fin_semana.py`, que debe crear su checkpoint. El siguiente ciclo llama al mismo script con la nueva fecha objetivo.

El run `45158022768` de la jornada ordinaria fue `success` a nivel job, pero `VENTANA_API_CHILE ... 07:39 ... FUERA_VENTANA`: procesamiento omitido. No interpretar `success` como éxito de ingestión. Pendiente validar en una próxima ejecución de fin de semana que `SIGUIENTE_JORNADA` se acompañe de un checkpoint creado y de procesamiento efectivo de la nueva fecha. No se dispararon workflows ni se alteró producción en esta revisión.

## Censo directo de archivos YAML en main (23/11)

Se enumeró directamente el endpoint GitHub Contents `.github/workflows/`: **74 archivos YAML**. Este censo reemplaza la lista documental parcial de 28 referencias; no acredita por sí solo que todos estén habilitados ni ejecutándose. Desglose por prefijo, solo clasificatorio:

### asistente (19)

`asistente-ia-adaptador-worker.yml`, `asistente-ia-auditoria-fragmentos-oc.yml`, `asistente-ia-auditoria-fuentes.yml`, `asistente-ia-backend-tests.yml`, `asistente-ia-comparar-pages.yml`, `asistente-ia-conexion-demo.yml`, `asistente-ia-consultas-reales.yml`, `asistente-ia-datos-reales.yml`, `asistente-ia-escenarios-analiticos.yml`, `asistente-ia-flujo-conversacional.yml`, `asistente-ia-flujo-local.yml`, `asistente-ia-intencion-gemini.yml`, `asistente-ia-lenguaje-natural.yml`, `asistente-ia-navegador.yml`, `asistente-ia-orquestador.yml`, `asistente-ia-post-chat.yml`, `asistente-ia-pruebas-motor.yml`, `asistente-ia-ui-aislada.yml`, `test-asistente-gemini.yml`.

### validaciones (27)

`validacion-mer.yml`, `validar-ajustes-landing-v2.yml`, `validar-analitica-historicos-v2.yml`, `validar-apertura-noviembre-2026.yml`, `validar-api-diaria.yml`, `validar-api-escalable.yml`, `validar-api-nocturna.yml`, `validar-api-preconciliacion.yml`, `validar-buscador-global-v2.yml`, `validar-busqueda-v2.yml`, `validar-cierre-historico-automatico.yml`, `validar-combinaciones-busqueda-v2.yml`, `validar-comparador-v2.yml`, `validar-conciliacion-diferida.yml`, `validar-cron-api-local.yml`, `validar-disparador-api-ubuntu.yml`, `validar-etl-fuentes-independientes.yml`, `validar-favoritos-csv-v2.yml`, `validar-paquete-analitico-v2.yml`, `validar-participantes-v2.yml`, `validar-perfiles-v2.yml`, `validar-presentacion-detalle-v2.yml`, `validar-rotacion-mensual.yml`, `validar-ux-integral-v2.yml`, `validar-ventana-api-nocturna.yml`, `verificar-acceso-gha-mer.yml`, `verificar-publicacion-diaria-v2.yml`.

### resto (28)

`ampliar-busqueda-v2.yml`, `api-compra-agil-400-actions.yml`, `api-mer-ejecucion-excepcional-20261028.yml`, `auditar-esquema-api-20261028.yml`, `auditoria-montos-operativos.yml`, `compra-agil-recuperacion-domingo.yml`, `compra-agil-recuperacion-sabado.yml`, `conciliar-multimes-ca-oc-v2.yml`, `etl-loba-puntual.yml`, `generar-analitica-v2.yml`, `indexar-relaciones-v2.yml`, `licitaciones-api-1615-actions.yml`, `observacion-api-2230.yml`, `preview-frontend-v2.yml`, `probar-campos-api-mer.yml`, `prueba-enriquecimiento-mer-20261028.yml`, `publicacion-v2-post-etl.yml`, `publicar-api-octubre-recuperacion.yml`, `publicar-autocompletado-v2.yml`, `publicar-frontend-v2.yml`, `publicar-oc-candidatas-v2.yml`, `publicar-participacion-v2.yml`, `publicar-perfiles-v2.yml`, `publicar-relaciones-procesos-v2.yml`, `publicar-sugerencias-global-v2.yml`, `reconstruir-seleccionados-20261029.yml`, `reparacion-mer-octubre-20261028.yml`, `reparar-analitica-organismos-v2.yml`.

**Disparadores verificados en YAML:** `licitaciones-api-1615-actions.yml` solo `workflow_dispatch` (cron externo Ubuntu); `observacion-api-2230.yml` solo `workflow_dispatch` (no confundir nombre con horario activo); `conciliar-multimes-ca-oc-v2.yml` manual y push de scripts; `publicacion-v2-post-etl.yml` workflow_run, push de datos, cron de comprobación `0,15,30,45 20,21 * * 1-5` y manual. `api-compra-agil-400-actions.yml` dos cron UTC 01:05/02:05 y manual, con filtro de ventana chilena. Recuperaciones sábado y domingo usan cron doble UTC y manual.

**Pendiente de censo completo:** consultar registro de workflows habilitados/deshabilitados, todos los disparadores de los 74 YAML, ejecuciones y contrastar cron/systemd local. No afirmar que 74 workflows estén activos. La causa del `KeyError` de recuperación ya tiene arreglo presente en los YAML de sábado/domingo, pero falta ejecución posterior que confirme tránsito entre jornadas.
