# Cierre de carga histórica — 16 de octubre de 2026

## Registros importados y verificados en Google Sheets
- **Procesos:** 10.000 códigos únicos (octubre 821, septiembre 6.917, agosto 2.262).
- **Resultados:** 3.046 registros de adjudicación informada en CSV, sin afirmar contrato ni OC verificada.
- **Ofertas:** 20.000 registros de licitaciones, vinculados a 4.480 procesos existentes; 12.994 con importe recuperable al tratarse de una única línea; 990 con indicador de selección en las filas fuente.

## Criterio conservador de Ofertas
Fuente: ZIP oficiales de licitaciones agosto–octubre de 2026. Se excluyeron identificadores de proveedor ausentes, fechas de envío posteriores a 2026-10-16, procesos fuera de los 10.000 existentes y combinaciones proceso+CódigoProveedor con más de un nombre o fecha de oferta. Se tomó como máximo una oferta por proceso y CódigoProveedor.

El archivo de licitaciones contiene importes **por línea** de producto. Por eso solo se conservó `monto_ofertado_clp` cuando el grupo tenía exactamente una fila y moneda peso chileno/CLP; para grupos multilínea el monto quedó vacío en lugar de fabricar un total.

**`id_cotizacion` queda vacío en las 20.000 ofertas históricas**, porque corresponde al identificador de API Compra Ágil y no existe de forma equivalente en estas filas de licitación. El dato `CodigoProveedor` original se utilizó para construir el lote sin mezclarse con `id_cotizacion`. Esta decisión preserva la fidelidad de las columnas, pero limita la identificación persistente de ofertas históricas mediante el esquema público actual: el registro visible debe tratarse como oferta por proveedor/proceso, no como una ID de oferta demostrada por la API.

Se priorizaron los procesos más recientes hasta alcanzar 20.000; no se infiere que las demás ofertas históricas no existan. Las 990 marcas `seleccionado` reflejan el CSV de líneas y no certifican adjudicación contractual.

## Pendientes de despliegue
1. Publicar un nuevo snapshot de Sheets en GitHub Pages.
2. Integrar los ETL de procesos y detalle en una ejecución diaria coordinada, con tres intentos y fechas pendientes para el día siguiente.
3. Activar cron tras la preparación de la recuperación; conservar la distinción de selección, adjudicación informada y OC verificada.
