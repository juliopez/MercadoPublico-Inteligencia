# Archivo histórico · Observatorio V1

La **primera versión (V1)** fue un prototipo de corta duración. El 4 de noviembre de 2026 se retiró del sitio activo y se declaró **V2 como única plataforma oficial**.

- `index.html`: fuente original del prototipo V1, preservada para consulta histórica.
- `observatorio.json`: último manifiesto V1, preservado para trazabilidad. Sus 51 fragmentos voluminosos se retiraron de `main` por obsolescencia. **No forman parte de la plataforma V2 ni se publican en GitHub Pages**.
- Se puede recuperar íntegramente la antigua V1 desde el historial Git anterior al retiro de archivos (por ejemplo, commit `6d3a976820bf0613a931c2359fdbe5cf8c0dbe34`). Su archivo HTML aquí conservado no pretende funcionar sin sus datos históricos.
- La plataforma vigente se publica en <https://juliopez.github.io/MercadoPublico-Inteligencia/>.
- La dirección antigua de V2, `/frontend-v2/`, redirige a la portada principal.

## Criterio de limpieza

Se retiraron **51 fragmentos exclusivos de V1, equivalentes a 137.528.681 bytes (aprox. 137,5 MB decimales) del árbol de trabajo actual**, y su manifiesto original. La historia Git conserva los objetos de versiones anteriores: **borrarlos de `main` no reduce por sí mismo el almacenamiento histórico de GitHub**. No se reescribió el historial para proteger trazabilidad.

Los aproximadamente 1,34 GB de JSON bajo `frontend-v2/data/` **se conservaron**, porque integran el catálogo público, las búsquedas indexadas, relaciones, perfiles e históricos de la V2. Borrarlos por tamaño rompería el Observatorio.

La migración dejó intactos el ETL Ubuntu de las 16:00, Google Sheets y sus esquemas, los flujos API, la rotación de mes y la conciliación oficial.
