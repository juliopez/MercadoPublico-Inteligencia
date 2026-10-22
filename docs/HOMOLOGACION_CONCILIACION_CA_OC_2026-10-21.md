# Homologación conciliación multientidad CA–OC: junio, julio, septiembre 2026

**Fecha:** 21–22 octubre 2026. **Estado:** implementación publicada en `main`; salida integral de los tres meses todavía no confirmada. Agosto queda como línea base y no se vuelve a ejecutar.

## Contexto

La conciliación original de agosto (`scripts/conciliar_agosto_ca_oc_v2.py`) utiliza Procesos, Ofertas seleccionadas, Resultados y OC de todos los meses públicos, y diferencia vínculos exactos por `codigo_proceso` de OC candidatas por misma unidad compradora y proveedor. Las candidatas **no acreditan** relaciones contractuales.

La auditoría adicional de ZIP COT ya cerró **240.649 vínculos oficiales explícitos**; después se incorporaron a MER **1.411 vínculos adicionales con referencias textuales en ZIP OC**, y se verificaron en Ubuntu. El archivo `frontend-v2/data/vinculos-oc-verificados.json` contiene 1.412 evidencias documentales; no repetir esas escrituras.

## Implementación homologada

- Nuevo script `scripts/conciliar_multimes_ca_oc_v2.py`: reutiliza las reglas del motor original de agosto y acepta `--periodo 2026-06|2026-07|2026-09`.
- Workflow `.github/workflows/conciliar-multimes-ca-oc-v2.yml`: valida sintaxis y totales contra catálogo, ejecuta los tres meses y publica índices separados en `frontend-v2/data/conciliacion/AAAA-MM/{directos,candidatos}/` y `resumen.json`.
- Los índices son **derivados y exploratorios**; no se incorporan las candidatas a `VinculosCOT_OC`, ni se modifica `codigo_proceso`.
- Se conservan V1, V2 operativo, MER, cron diario, ETL, ZIP oficiales y conciliación anterior de agosto.

## Criterios de cierre

1. Confirmar ejecución exitosa del workflow y existencia de los tres `resumen.json` con conteos acordes al catálogo; revisar conflictos y registros de candidatos ambiguos.
2. Mantener **separada** la evidencia documental verificada de los candidatos estadísticos.
3. Documentar resultados cuantitativos y contrastar el alcance con agosto sin comparar directamente candidatos estadísticos con vínculos acreditados.
4. No presentar CI como aprobación visual ni efectuar cargas históricas.
5. Si se requiere mostrar los índices nuevos en V2, auditar primero el código consumidor; la publicación de JSON no garantiza por sí sola visualización.

**Pendiente real:** la ejecución en Actions y sus resultados aún no se verificaron durante la creación del workflow. Esta nota acredita solo implementación publicada, no homologación de datos finalizada.
