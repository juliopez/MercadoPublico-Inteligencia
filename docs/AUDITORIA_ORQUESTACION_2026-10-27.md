# Auditoría diaria — martes 27 de octubre de 2026

## Resultado

**Cadena pública GitHub de hoy: comprobada y exitosa.** La ejecución local detallada de Ubuntu/Sheets/conciliación permanece pendiente de contrastar con logs de la máquina. No se realizaron reejecuciones, escrituras ni cambios de configuración durante esta auditoría.

## Tiempos (America/Santiago, UTC-3)
- 16:10:57.981: fecha_publicacion del catálogo público octubre.
- 16:11:12: commit origen desde MER Ubuntu Publisher `dedcb47bd137356597dc66e015b6a967f52dc445`.
- 16:11:24: inicio de `Publicacion V2 posterior al ETL Ubuntu`, ejecución [40566833917](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/40566833917), evento `push`, resultado `success`. Pasos de comprobación del origen, generación/validación de derivados y publicación: **success**; ninguno omitido.
- 16:11:59: commit de derivados `83e6e18428de43028a45105e5a6a1a43baa7c4ae`.
- 16:12:07: inicio de `Observatorio - vista previa frontend MER v2`, ejecución [40566943927](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/40566943927), evento `workflow_run`, **success** incluyendo `Desplegar preview v2 manteniendo raíz v1`.
- 16:12:07: inicio de `Supervisar publicación diaria MER V2`, ejecución [40566944013](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/40566944013), evento `workflow_run`, **success**, paso `Verificar actualidad del MER y de los índices` successful.
- 16:11:24: otra ejecución de Pages por `push` [40566833930](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/40566833930), **success**. No implica error, pero puede redundar con el posterior `workflow_run`.
- El disparador `schedule` de supervisión independiente de las 18:12 del día 27 **no aparece en los runs consultados**. No se debe afirmar su éxito; el supervisor por evento sí funcionó.

## Integridad de conteos al consultar main
| Entidad | 26/10 | 27/10 | Cambio neto |
|---|---:|---:|---:|
| Procesos | 2619 | 3184 | +565 |
| Órdenes de compra | 125133 | 133202 | +8069 |
| Ofertas | 0 | 0 | 0 |
| Resultados | 0 | 0 | 0 |

- La analítica `frontend-v2/data/analitica/2026-10/procesos.json` informa 3184 registros, 1429 con monto y CLP 42.871.843.588.
- La analítica `frontend-v2/data/analitica/2026-10/ordenescompra.json` informa 133202 registros, todos con monto y CLP 1.329.991.367.752.
- Analítica = catálogo para Procesos y OC, y los workflows validaron partes y datos derivados.

## Evidencias que faltan y alcance de la certificación
1. Confirmar `logs/arranque_integrado_20261027*.log`, `logs/orquestador_integrado_20261027*.log`, `salida_operativa/estado_sincronizacion.json` y `estado_conciliacion.json` en Ubuntu, para certificar invocación exacta del cron, escritura en Sheets, conciliación y resultado de salida. El commit automático Ubuntu es evidencia fuerte de publicación, pero no prueba independiente de todas esas fases.
2. No se obtuvo respuesta HTTP independiente de los JSON servidos por Pages desde el entorno de auditoría; el job de deploy sí finalizó success.
3. El scheduler de GitHub a las 18:12 puede omitir o retrasar disparos. La supervisión por evento es positiva; no sustituye detección externa de silencio si falla toda la cadena.

## Dictamen
**Publicación desatendida en GitHub y regeneración/supervisión por evento validadas para el 27/10.** Para declarar toda la Etapa 1 como verificada extremo a extremo falta evidencia local de Ubuntu, persistencia y conciliación; y comprobación HTTP si se exige certificar contenido servido. No iniciar API Compra Ágil antes de cerrar lo pendiente de Etapa 1.

## Cierre formal — evidencia local aportada el 27/10, 19:01 Santiago

El operador ejecutó una auditoría de solo lectura en Ubuntu y aportó capturas completas del resumen de terminal. Se verifica:

- Servicio `cron`: `active`, entrada `0 * * * * .../ubuntu_cron_integrado.sh --cron`. La guardia interna del script limita ejecución a lunes–viernes a las 16:00.
- Archivo `logs/arranque_integrado_20261027_160001.log`: `ARRANQUE_CRON fecha=2026-10-27T16:00:01-03:00 modo=--cron`.
- Archivo `logs/orquestador_integrado_20261027_160001.log`: `ORQUESTADOR inicio=2026-10-27T16:00:01-03:00 periodo=2026-10` y `ORQUESTADOR OK: 2026-10-27T16:11:22-03:00`.
- `estado_sincronizacion.json`: `EXITOSA`, `codigo_salida=0`, `ejecucion_chile=2026-10-27T16:05:59.357315-03:00`. ZIP oficiales licitaciones y OC con URL de fuente, SHA256 y marca de verificación. Tablas: Procesos 565 nuevos / 110 modificados / 2509 sin cambios; OrdenesCompra 8069 nuevos / 8523 modificados / 115274 sin cambios; Proveedores 725 nuevos / 0 modificados / 21523 sin cambios.
- `estado_conciliacion.json`: `CONCILIACION_VERIFICADA`, motivo «Conciliacion y lectura posterior verificadas», timestamp 2026-10-27T19:10:45.658584+00:00 (16:10:45 Chile).
- Publicación del orquestador `PUBLICACION_V2_OK_O_SIN_CAMBIOS`, commit origen `dedcb47` a las 16:11:12 Chile.
- Verificación HTTP externa desde Ubuntu: `catalogo-publico.json`, `analitica/2026-10/procesos.json` y `analitica/2026-10/ordenescompra.json`, los tres **HTTP 200**. Catálogo: 3184 Procesos, 133202 OC, Ofertas 0, Resultados 0; analítica coincide (3184 y 133202).
- GitHub Actions auditados previamente: derivados run `40566833917`, supervisor por evento run `40566944013`, Pages run `40566943927`, todos completos y `success`, sin pasos críticos omitidos.

### Dictamen definitivo de Etapa 1

**ETAPA 1 CERRADA Y VALIDADA** para la cadena diaria vigente licitaciones/OC → MER (éxito informado por ETL y verificación local) → conciliación COT–OC → exportación → GitHub → derivados → supervisor por evento → Pages y lectura HTTP de los JSON públicos. Ejecución del 27/10 comprobada sin reejecución manual ni nuevas cargas durante la auditoría.

Observaciones no bloqueantes:
1. El programador independiente de GitHub Actions de las 18:12 no tiene una ejecución del 27/10 visible en la auditoría, pero el supervisor por evento sí ejecutó y aprobó controles.
2. La revisión es evidencia operativa del sistema y lectura posterior registrada, no auditoría externa fila por fila del Google Sheet privado.
3. Ofertas y Resultados de octubre siguen sin cobertura automatizada; corresponde a Etapa 2, no se interpreta como cero actividad oficial.
4. No se autoriza por este cierre activar cierre mensual irreversible ni modificar históricos.

La Etapa 2 queda habilitada para iniciar con auditoría técnica de fuentes/API sin alterar la cadena diaria probada.
