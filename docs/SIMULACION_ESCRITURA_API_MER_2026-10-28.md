# Etapa 2 — simulador offline de escritura API → MER

**Base operativa:** cron Ubuntu 16:00 → ETL ZIP Licitaciones/OC → conciliación COT–OC → MER → exportador V2 → publicación GitHub → índices/analítica → Pages, cadena validada el 27/10. **No reemplazar ni reordenar esta cadena.**

## Entrega
- `scripts/simular_escritura_api_mer.py`: simula enriquecimiento sin importar gspread, sin autenticación, sin llamadas API y sin escribir Sheets.
- Entrada: transformación JSON privada preexistente y snapshot JSON privado con cabeceras/filas de `Ofertas`, `Resultados` y `Proveedores`.
- Resolver la identidad por RUT usando `Proveedores` existente, calcular inserciones, actualizaciones, sin cambios y conflictos mediante el planificador vigente.
- Salida únicamente **conteos agregados**, sin PII, `aplicable=false` obligatorio.
- `tests/test_simular_escritura_api_mer.py`: escenarios sintéticos de inserción y rechazo ante ausencia de snapshot.

## Ejemplo (offline)
```bash
python3 scripts/simular_escritura_api_mer.py \
  --transformacion /ruta/privada/transformadas/839-4-COT26.json \
  --snapshot /ruta/privada/snapshot_tres_tablas.json
```

## Próximo tramo condicionado
1. Validar CI del simulador y exportación preview (sin datos reales).
2. Diseñar un escritor protegido con respaldo completo, lock compartido `logs/.mer_escritura_compartida.lock`, checkpoint externo a las seis tablas y lectura posterior.
3. Revisar consumidor/frontend y ampliar exportador **sin habilitar publicación** hasta completar ensayos de extremo a extremo.
4. Capturar un único JSON real privado y ejecutar simulador, únicamente cuando la cadena esté preparada.

**No se han realizado consultas nuevas a ChileCompra, escrituras en el MER, modificaciones del cron ni despliegues de datos de prueba.**
