# Etapa 2 — Pretransacción API–MER, sin escrituras — 28/10/2026

## Base mantenida
La orquestación verificada el 27/10 permanece intacta. No se consultó API ChileCompra ni se escribieron registros en Sheets ni datos de frontend.

## Implementación nueva
- `scripts/preparar_transaccion_api_mer.py`: recibe una transformación ya almacenada y un snapshot privado de las tres tablas `Ofertas`, `Resultados`, `Proveedores`. Utiliza el mismo nombre de lock existente `logs/.mer_escritura_compartida.lock` que el conciliador (`fcntl.flock LOCK_EX|LOCK_NB`) **solo para ensayar el preflight**.
- Determina filas nuevas, campos completables, duplicados y conflictos a través de los componentes previamente incorporados. Bloquea la prueba si no existe el lock compartido o está ocupado. No incorpora cliente de Sheets ni parámetro `--aplicar`.
- Produce respaldo local con permisos `0600` y SHA-256 del snapshot, y emite únicamente conteos y resumen sin PII. No sube snapshots a GitHub, Actions o Pages.
- `tests/test_preparar_transaccion_api_mer.py`: pruebas sin HTTP de planificación y lock existente.

## Instrucciones para ejecutar **offline**, solo con snapshots privados autorizados
```bash
python3 scripts/preparar_transaccion_api_mer.py \
  --transformacion /ruta/privada/transformadas/839-4-COT26.json \
  --snapshot /ruta/privada/snapshot_tres_tablas.json \
  --lock logs/.mer_escritura_compartida.lock \
  --respaldo /ruta/privada/respaldos/preflight_api_20261028.json
```

## Importante
Este código **NO ES UN ESCRITOR DE PRODUCCIÓN**. Aún faltan transacción de Sheets, lock sostenido durante toda la escritura, respaldo completo verificable del libro, relectura posterior, recuperación ante interrupción y comprobación de compatibilidad del consumidor de frontend. Tampoco están activadas en el publicador las entidades `ofertas` y `resultados`: el ensayo aislado de fragmentos no equivale a despliegue.

Antes de habilitar `--aplicar`: probar con libro separado, validar conflictos y claves de Resultados, y determinar control consistente de errores parciales de API/Sheets.
