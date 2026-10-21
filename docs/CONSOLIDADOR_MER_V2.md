# Consolidación MER v2 — arquitectura por catálogo

## Decisión de carpetas

Mantener `01_Historicos_MER` (meses aprobados, inmutables) y `02_Operativo_MER` (mes vigente y hojas futuras preparadas). La localización en Drive es **organizativa**, no una regla para determinar qué se publica.

## Selección de períodos

`config/catalogo_sheets.json` es la fuente de identificadores. Por cada período, seleccionar como máximo una hoja:
- Históricos solo si están auditados.
- Operativo **solo si su período coincide con el calendario vigente en America/Santiago**.
- Hojas de meses futuros preparadas y operativos de meses anteriores **no se publican** automáticamente.
- Al cerrar un mes, reemplazar su entrada en catálogo por la histórica aprobada. No mantener dos referencias publicables al mismo período.

Herramienta disponible: `python scripts/planificar_consolidacion_mer.py` genera `salida_operativa/plan_consolidacion.json` sin conectar con Google ni modificar el frontend.

## Contrato real del frontend

El frontend actual carga `data/observatorio.json` con `fecha_actualizacion`, `conteos` y `partes`, o en su defecto `tablas`; espera cuatro entidades: `procesos`, `ofertas`, `resultados` y `ordenescompra`. En `partes` solo admite rutas `data/partes/observatorio-[a-z]+-[0-9]{4}.json`. Esta expresión limita la segmentación actual; no renombrar fragmentos sin cambiar y probar el lector.

El MER v2 almacena seis entidades; Proveedores y VinculosCOT_OC son soporte de relaciones, no tablas mostradas de forma independiente en el frontend actual. Las cuatro tablas visibles deben conservar campos, cardinalidades y semántica, incluidos los estados de verificación.

## Estrategia de exportación pendiente

1. Leer Google Sheets de manera paginada, controlar errores de API y validar cabeceras.
2. Establecer deduplicación técnica por `(periodo, tabla, pk)`, preservando los códigos repetidos entre meses como eventos/fotografías históricas hasta definir precedencia explícita. No afirmar unicidad global.
3. Producir fragmentos de JSON en directorio temporal y manifiesto, validar conteos/hash y recién publicar de forma íntegra.
4. Mostrar última publicación y última sincronización **por fuente**, sin atribuir a Compra Ágil actualizaciones que no ha recibido.
5. **Rendimiento**: hay millones de registros entre las seis tablas de junio-septiembre. El frontend actual acumula todos los fragmentos en memoria. Antes de exportar todo, validar tamaño, memoria y navegación; probablemente requiera carga selectiva por período y búsqueda sobre índices estáticos. No desplegar un JSON gigante solo por funcionar el generador.

## Estado
Solo planificador de selección implementado y publicado. **No se han leído las bases por este módulo ni construido/publicado JSON finales.** El ETL cron y el frontend permanecen sin cambios.
