# GitHub Actions — mapa de mantenimiento

Este directorio contiene **publicaciones, ETL, generación de índices y suites de prueba**. Los archivos se conservan por seguridad hasta comprobar dependencias; no debe borrarse un workflow solo por parecer antiguo.

## 1. Publicación y operación (proteger)
- `front-pages.yml`, `publicar-frontend-v2.yml`, `preview-frontend-v2.yml`: páginas y vistas públicas.
- `publicar-sheets-pages.yml`, `publicar-solo-sheets.yml`, `observatorio-unico.yml`, `etl-loba-puntual.yml`: integraciones/operación; **verificar uso antes de tocar**.

## 2. Generación de datos V2 (proteger)
- `generar-analitica-v2.yml`: perspectivas mensuales de montos y actores.
- `publicar-relaciones-procesos-v2.yml` y `indexar-relaciones-v2.yml`: índices de vínculos.
- `publicar-perfiles-v2.yml`, `publicar-autocompletado-v2.yml`, `publicar-sugerencias-global-v2.yml`, `ampliar-busqueda-v2.yml`: agregados y sugerencias.

## 3. Validación continua
- **Integración actual:** `validar-analitica-historicos-v2.yml`, `validar-ux-integral-v2.yml`, `validar-busqueda-v2.yml`, `validacion-mer.yml`.
- **Pruebas específicas acumuladas:** `validar-ajustes-landing-v2.yml`, `validar-buscador-global-v2.yml`, `validar-combinaciones-busqueda-v2.yml`, `validar-comparador-v2.yml`, `validar-favoritos-csv-v2.yml`, `validar-paquete-analitico-v2.yml`, `validar-perfiles-v2.yml`, `validar-presentacion-detalle-v2.yml`.

Las suites específicas quedan etiquetadas como **candidatas de consolidación**, no como eliminadas ni deshabilitadas. Una consolidación futura requiere verificar qué pruebas cubre efectivamente cada suite, si corre por `push`, `workflow_dispatch` u otro evento, y si afecta rama `main` o Pages.

## Procedimiento de limpieza segura
1. Leer [README principal](../README.md), [decisiones](../docs/DECISIONES_TECNICAS.md) y [bitácora de mantenimiento](../docs/MANTENIMIENTO_REPOSITORIO_2026-10-21.md).
2. Obtener lista de archivos y eventos actuales; revisar últimas ejecuciones y dependencias.
3. Proponer lista exacta de archivos redundantes con reemplazo y rollback.
4. Eliminar solo tras verificación de sustitución y aprobación del alcance.
5. Probar publicación V1/V2 e índices después de cualquier eliminación.

**No borrar:** ramas de respaldo, datos públicos, workflows de publicación/operación ni pruebas cuya cobertura no se haya demostrado redundante.
