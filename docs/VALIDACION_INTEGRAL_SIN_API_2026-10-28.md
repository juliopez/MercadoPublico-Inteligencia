# Etapa 2 — Ensayo de flujo completo sin API

## Evidencias ejecutadas
1. **Copia real separada de Google Sheets:** `18iPCaHbNTpjIfgMsNu3ZhQ0u9lBqx4_zaDdWgrSkcqY`, cabeceras de Ofertas y Resultados verificadas. Se insertaron dos filas **sintéticas** mediante conector de Sheets y se releyeron ambas; no se utilizó el cliente Python de Ubuntu.
2. **Pruebas offline del escritor:** CI previo `40790735940`, concluido con éxito. Protecciones sobre ID del catálogo y allowlist `MER_API_TEST_SHEET_ID`.
3. **Prueba integral añadida:** `tests/test_integracion_api_mer_sin_api.py` simula una falla entre las escrituras de Ofertas y Resultados, conserva respaldo, reintenta sin duplicar, verifica tercera ejecución sin cambios, exporta archivos JSON para ambos tipos con `exportar_ofertas_resultados_preview.py` y exige que no contengan RUT ni `id_proveedor`.
4. CI de la nueva prueba: https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/40790921461. Confirmar conclusión antes de certificar.

## Pendiente real antes de consulta a API
- La **cuenta de servicio local Ubuntu** aún no se ha utilizado contra una copia real; no es correcto llamar validado al escritor Python en Google Sheets basándose en la inserción mediante el conector.
- La prueba de exportación produce fragmentos aislados pero **no ejecuta el despliegue real de Pages**; tampoco se modificó el publicador operativo que exporta solo Procesos y OC.
- El rollback automático no está implementado; en caso de fallo parcial, debe intervenir una operación de recuperación supervisada con el respaldo local.
- No se consultó la API ChileCompra ni se alteró el cron, la hoja operativa o el frontend público.

## Gate
Se requiere CI verde y ensayo final con cuenta de servicio antes de autorizar consulta y carga API real.
