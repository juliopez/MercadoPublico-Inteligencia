# Inventario técnico de fuentes públicas para el Asistente IA V2

Fecha: 13/11/2026. Estado: **revisión documental y lectura de archivos en GitHub; sin cambios productivos**.

## 1. Fuentes verificadas
| Fuente | Ruta / contrato | Contenido y utilidad | Precaución |
|---|---|---|---|
| Catálogo | `frontend-v2/data/catalogo-publico.json` | `fecha_publicacion`, `periodos[]`, `tipo`, `conteos`, `partes` | Catálogo de verdad para disponibilidad y totales |
| Agregados por entidad | `frontend-v2/data/analitica/YYYY-MM/{procesos,ofertas,resultados,ordenescompra}.json` | `registros`, `registros_con_monto`, `monto_total_clp`, `top_actores`, `top_actores_monto`, `campo_monto` | Totales de registros; top 10 no es ranking completo |
| Modalidades | `frontend-v2/data/analitica/YYYY-MM/procesos.json` | `modalidades` pares [nombre, cantidad] | Suma debe coincidir con `registros` y catálogo |
| Procesos únicos y organismos | misma ruta de procesos | `procesos_unicos`, `modalidades_unicas`, `organismos_procesos_unicos` | `organismos_procesos_unicos` es listado por nombre; no identidad legal unificada |
| Búsqueda global | `frontend-v2/data/busqueda/` y `frontend-v2/js/busqueda-global.js` | Índices de candidatos y verificación selectiva de fragmentos | No suponer que el índice por sí solo confirma coincidencias |
| Sugerencias y facetas | `frontend-v2/data/sugerencias/YYYY-MM/{entidad}/facetas.json`, índices por prefijo | Estados, modalidades y sugerencias | Sugerencias no son resultados exhaustivos |
| Perfiles por proveedor | `frontend-v2/data/perfiles/YYYY-MM/{ofertas,resultados,ordenescompra}/{shard}.json` | Perfil por nombre normalizado | Shard derivado del primer byte SHA-256 del nombre canónico |
| Participación por proveedor | `frontend-v2/data/participacion/YYYY-MM/proveedor/{shard}.json` | Códigos participados/seleccionados y montos asociados | Selección registrada no equivale a adjudicación contractual |
| Relaciones | `frontend-v2/data/relaciones-procesos/` | Índices de relación entre entidades | Confirmar contratos exactos antes de consumir |
| Fragmentos originales | `frontend-v2/data/partes/{entidad}/YYYY-MM/NNNN.json` | Evidencia por registro y enlaces originales | Leer selectivamente, nunca todos por consulta ordinaria |

## 2. Validación de agregados
Se consultaron directamente los archivos de analítica de procesos para los seis meses del catálogo, con igualdad entre `registros` y `conteos.procesos`.

| Período | Licitaciones | Compra Ágil | Procesos |
|---|---:|---:|---:|
| 2026-06 | 8.649 | 72.249 | 80.898 |
| 2026-07 | 8.196 | 72.803 | 80.999 |
| 2026-08 | 8.230 | 75.714 | 83.944 |
| 2026-09 | 6.974 | 72.459 | 79.433 |
| 2026-10 | 6.895 | 85.407 | 92.302 |
| 2026-11 | 1.458 | 7.620 | 9.078 |

**Importante:** este contraste comprueba consistencia de agregados, no completitud de Mercado Público ni vigencia futura. Noviembre es operativo; cobertura parcial y recargas posibles.

## 3. Ejemplo de contrato: procesos agosto
Archivo `data/analitica/2026-08/procesos.json`:
- `version=3`, `periodo=2026-08`, `entidad=procesos`, `registros=83944`, `procesos_unicos=83944`.
- `modalidades=[["Compra Ágil",75714],["Licitación",8230]]`.
- `organismos_procesos_unicos`: 1.975 entradas con `organismo`, `procesos`, `licitaciones`, `compras_agiles`, `otras`, `con_monto`, `monto`.
- Las entidades ofertas, resultados y OC tienen `top_actores` y `top_actores_monto`, pero no `organismos_procesos_unicos`.

## 4. Estrategia de consultas
1. **Directas por agregado:** conteos por período/modalidad, comparación temporal, montos por entidad, top 10 de actores y consulta exacta de organismo si existe en `organismos_procesos_unicos`.
2. **Índices especializados:** proveedor, participación, comparación de proveedores y relaciones. Confirmar estructura de cada índice y validaciones del frontend antes de programar.
3. **Búsqueda por palabras clave y filtros combinados:** índice para candidatos + lectura selectiva de registros; limitar coste y número de coincidencias.
4. **No soportadas sin nuevo derivado o comprobación:** preguntas arbitrarias que exijan barrer todos los fragmentos, ranking completo de proveedores, inferencia de pagos o adjudicaciones sin evidencia.
5. **Caché:** invalidar según versión/fecha de publicación del catálogo y evitar mezclar generaciones de agregados.

## 5. Fase 1: pendientes técnicos
- Versionar el código del Worker en un directorio aislado con pruebas; Cloudflare sigue siendo el lugar de despliegue.
- Validación de entradas e intenciones con esquemas enumerados, límites de tiempo y tamaño, caché.
- Protección real contra abuso y límites de solicitudes: CORS no basta.
- Manejo de errores con códigos y observabilidad sin registrar preguntas completas.
- Pruebas automáticas con respuestas conocidas y negativas; no exponer el chat en el frontend antes de auditoría.

## 6. Protección operativa
Inventario y planificación solamente. **No se modifica** ETL, cron 09:00/16:00/16:15/22:05, MER/Google Sheets, índices publicados, frontend ni Worker de Cloudflare.

## Referencias
- [Plan integral aprobado](ASISTENTE_IA_OBSERVATORIO_V2.md)
- [Modelo de datos](../MODELO_DATOS.md)
- [Frontend V2](../../frontend-v2/README.md)
- [Generador de analítica](../../scripts/generar_analitica_v2.py)
