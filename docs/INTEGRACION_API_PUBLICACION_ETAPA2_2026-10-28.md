# Integración Etapa 2 — Escritura y publicación de Ofertas/Resultados

## Estado comprobado
Se verificó código operativo actual, sin nuevas consultas API ni cambios de cron.

- `scripts/exportar_mer_operativo_v2.py` exporta exclusivamente `Procesos` y `OrdenesCompra` (constante `MAP`), aunque el catálogo contemple cuatro entidades.
- `scripts/ubuntu_publicar_v2_post_etl.sh` sólo añade a Git los fragmentos de `procesos` y `ordenescompra` y requiere una ejecución fresca del ETL principal después de las 16:00.
- El workflow de derivados `.github/workflows/publicacion-v2-post-etl.yml` genera índices, perfiles y analítica **solo** para esos dos tipos y valida sus conteos. Sus dependencias y triggers no deben alterarse hasta validar el flujo ampliado.
- Una eventual escritura de Ofertas/Resultados en Sheets **no aparecerá automáticamente en Pages** mediante las rutas actuales.

## Trabajo realizado en esta intervención
- `scripts/planificar_upsert_api_mer.py`: planificador offline para nueve columnas Ofertas/diez Resultados, con claves `(codigo,id_cotizacion)` y `(codigo,id_cotizacion_ganadora)`, detección de duplicados y conflictos. Conserva los valores ya verificados, y propone completar sólo los vacíos; **no escribe Sheets**.
- `tests/test_planificar_upsert_api_mer.py`: casos sintéticos de idempotencia, duplicados, conflicto y cabeceras.

## Limitación clave antes de activar escritura
- La clave de Resultados de una adjudicación V1 puede no contener `id_cotizacion_ganadora`; **no debe utilizarse este planificador de selección para adjudicaciones V1 sin una clave jurídica/documental compatible**.
- `id_proveedor` todavía requiere resolución de identidad mediante lectura de Proveedores y RUT canónico; no se permite generar IDs no contrastados.
- No se ha probado una ejecución con el JSON V2 real porque el sondeo API anterior sólo registró presencia de campos y **no conservó el contenido**.
- No se ha implementado el publicador ni el upsert aplicado; estos cambios implican modificar rutas productivas validadas, que deben pasar pruebas en seco y respaldo antes de habilitarse.

## Secuencia de habilitación
1. Resolver proveedor desde tabla existente y poner a prueba planner sobre copia/snapshot de Sheets.
2. Implementar escritor controlado, checkpoint externo y relectura posterior.
3. Ampliar exportador de forma compatible para las cuatro entidades públicas, validando PK, fragmentos, catálogo y rollback; resguardar la orquestación normal.
4. Extender el stage de Git a las dos carpetas y regenerar derivados bajo condiciones separadas para Ofertas y Resultados, sin regresión en Procesos/OC.
5. Validar con fixture → Sheets de prueba → JSON → Pages preview; sólo entonces activar piloto de producción.

**Dictamen:** transformación y plan de upsert desarrollados, integración de escritura y publicación todavía no activada. No confundir código preparado con datos desplegados.
