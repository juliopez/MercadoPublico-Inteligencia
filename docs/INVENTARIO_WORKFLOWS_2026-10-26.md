# Inventario preliminar de GitHub Actions — 26/10/2026

**Advertencia:** inventario basado en los 30 YAML presentes en `.github/workflows/` y en inspección parcial de sus disparadores. El estado real `active/disabled_manually/disabled_inactivity` de cada workflow **no se pudo consultar** desde la API de Actions. No equivale a inventario de desactivaciones, ni autoriza a desactivar funciones.

## Cadena diaria operativa identificada (mantener)
- `publicacion-v2-post-etl.yml`: derivados, `push` catálogo + `schedule` + `workflow_dispatch`.
- `verificar-publicacion-diaria-v2.yml`: supervisión, `workflow_run` + `schedule` + `workflow_dispatch`.
- `preview-frontend-v2.yml`: despliegue Pages V2, `push` + `workflow_run` + `workflow_dispatch`.

## Otros workflows observados (no asumir desactivados)
- `front-pages.yml`: despliegue separado de V1 por `push` del índice V1 o ejecución manual; conservar separación V1/V2.
- `validacion-mer.yml`: CI del modelo, `push`, PR y manual.
- `publicar-frontend-v2.yml`: exportación aislada por período/entidad, `push` filtrado y manual.
- `publicar-participacion-v2.yml`: índices de participación, `push` filtrado y manual.
- `generar-analitica-v2.yml`: generación específica de analítica, `push` filtrado y manual.

## Otros archivos presentes — clasificación funcional pendiente
- `ampliar-busqueda-v2.yml`
- `auditoria-montos-operativos.yml`
- `conciliar-multimes-ca-oc-v2.yml`
- `etl-loba-puntual.yml`
- `indexar-relaciones-v2.yml`
- `publicar-autocompletado-v2.yml`
- `publicar-oc-candidatas-v2.yml`
- `publicar-perfiles-v2.yml`
- `publicar-relaciones-procesos-v2.yml`
- `publicar-sugerencias-global-v2.yml`
- `validar-ajustes-landing-v2.yml`
- `validar-analitica-historicos-v2.yml`
- `validar-buscador-global-v2.yml`
- `validar-busqueda-v2.yml`
- `validar-combinaciones-busqueda-v2.yml`
- `validar-comparador-v2.yml`
- `validar-favoritos-csv-v2.yml`
- `validar-paquete-analitico-v2.yml`
- `validar-participantes-v2.yml`
- `validar-perfiles-v2.yml`
- `validar-presentacion-detalle-v2.yml`
- `validar-ux-integral-v2.yml`

## Regla de clasificación propuesta
- **OPERATIVO:** indispensable para una actualización desatendida.
- **AUXILIAR/MANUAL:** cumple una función puntual válida; puede permanecer habilitado sin disparador automático diario.
- **VALIDACIÓN/CI:** prueba de código, datos o interfaz; no confundir con ejecución del ETL.
- **HISTÓRICO:** reemplazado y sin dependencias; requiere justificar el reemplazo.
- **DESACTIVADO:** solamente tras confirmar estado real de GitHub Actions o retirar todos sus disparadores automáticos bajo control de versiones.

## Siguiente control antes de desactivar
1. Leer los 30 YAML y anotar disparadores, permisos, escrituras, relaciones `workflow_run`, ramas y ejecuciones recientes.
2. Consultar estados reales de workflows en GitHub Actions.
3. Verificar dependencias y preservar V1, V2, CI y tareas manuales necesarias.
4. Elaborar lista exacta de históricos candidatos; no eliminar ni desactivar antes de aprobar esa lista.
