# API V2 — conservación de JSON y transformación reutilizable — 28/10/2026

**Implementado en código, sin extracción real nueva ni escrituras MER.**

## Componentes
- `scripts/cache_y_transformar_compra_agil_mer.py`: modo por defecto **offline**, exige respaldo JSON en directorio externo al repositorio; `--fetch` activa explícitamente una sola consulta cuando el JSON aún no existe.
- `scripts/adaptar_detalle_compra_agil_mer.py`: adapta JSON a las columnas efectivas de `Ofertas` y `Resultados`, sin deducir adjudicación ni identidad canónica.
- `tests/test_cache_y_transformar_compra_agil_mer.py`: pruebas sintéticas de permisos privados, rechazo de sobreescritura, validación de códigos y reutilización.

## Operación — sin consultar API
```bash
python3 scripts/cache_y_transformar_compra_agil_mer.py \
  --codigo 839-4-COT26 --dir-privado "$HOME/.local/share/mercadopublico/api-v2"
```
**Importante:** este comando solo funciona si ya existe `$HOME/.local/share/mercadopublico/api-v2/respuestas/839-4-COT26.json`. La prueba de campos anterior no conservó ese JSON: devolverá `SIN_CACHE`, sin llamar a ChileCompra.

## Operación — nueva captura autorizada explícitamente para una ocasión posterior
```bash
CHILECOMPRA_TICKET=... python3 scripts/cache_y_transformar_compra_agil_mer.py \
  --codigo 839-4-COT26 --dir-privado "$HOME/.local/share/mercadopublico/api-v2" --fetch
```
Guardar el secreto en el entorno/gestor seguro, **nunca** en consola, código, argumentos guardados o documentación. Si el JSON ya existe, el modo `--fetch` lo reutiliza y no consulta la API.

## Protección
1. El JSON original y la transformación se guardan con permisos de archivo `0600`, bajo directorio `0700`, fuera del repositorio. No subir a GitHub, Pages o logs públicos.
2. Se valida `success`, código exacto del proceso, IDs de cotización y ausencia de selecciones ambiguas; se informa SHA256 para verificar identidad de la respuesta sin exponerla.
3. No permite sobreescritura de archivos existentes; una transformación revisada debe producirse tras respaldar/gestionar explícitamente el archivo transformado, manteniendo intacto el original.
4. Montos CLP permanecen vacíos salvo `--clp-verificado`, que solo corresponde después de demostrar la divisa del payload. No inferir adjudicación desde `proveedor_seleccionado`.
5. **Aún pendiente:** pruebas con JSON real conservado, conciliación de id_proveedor y upsert idempotente contra hojas MER. No se ha ejecutado una nueva llamada API ni se ha modificado el cron diario.

## Nota de arquitectura
No usar GitHub Actions como almacén persistente de respuestas confidenciales en ausencia de un control explícito de acceso, retención y cifrado. El lugar recomendado para esta primera etapa es el almacenamiento privado Ubuntu con política de respaldos y purga.
