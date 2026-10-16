# Paso 3: validación de Compra Ágil V2

## Configuración

En el repositorio, abre Settings > Secrets and variables > Actions > New repository secret. Asigna el nombre `CHILECOMPRA_TICKET` e introduce el ticket de ChileCompra (sin compartirlo en el código).

## Ejecución

En Actions, selecciona `Validar API ChileCompra` y luego `Run workflow`. Se consultarán cinco códigos de prueba. Los archivos JSON se conservarán como artefacto de esa ejecución por un día y no se publicarán en GitHub Pages.

## Próxima revisión

Verificar códigos HTTP, estructura de los resultados y disponibilidad efectiva de los datos de proveedores, ofertas y adjudicaciones. No incorporar datos reales al dashboard hasta validar campos y tratamiento de los llamados.

Fuente: https://www.chilecompra.cl/api/
