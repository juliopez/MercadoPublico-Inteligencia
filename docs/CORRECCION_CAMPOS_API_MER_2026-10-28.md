# Corrección de datos de Compra Ágil — 28 de octubre de 2026

## Causa verificada
Una inspección de **claves**, sin volcar identificadores ni cotizaciones de los proveedores, confirmó la estructura real de la API v2:
- Estado: `payload.estado.glosa`.
- Organismo comprador y región: `payload.institucion.organismo_comprador` y `nombre_region`.
- Presupuesto expresamente CLP: `payload.presupuesto.monto_disponible_clp`.
- Total de ofertas: `payload.resumen.total_ofertas_recibidas`.
- Identificador del proveedor en oferta: `payload.proveedores_cotizando[].codigo_empresa`.

Correcciones aplicadas a normalizador, adaptador y enriquecimiento por PK, preservando los valores ya existentes y sin alterar los cron/horarios.

## Ejecución de reparación
- GitHub Actions: https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/40809086068
- Resultado persistido `control/ultimo_reporte_api_mer.json`: **9 procesos enriquecidos**, **71 ofertas enriquecidas**, 0 procesos/ofertas/resultados nuevos, 1 error `APIError` de Google Sheets en proceso `608-6187-COT26`.
- El registro fallido fue reprogramado para revisión el 29-10-2026; no se repitieron consultas esta noche.
- Se exportó con el modo `--incluir-api`; generación de índices validada: https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/40809464001.
- Despliegue Pages: https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/40809514938. Confirmar resultado en Actions.

## Campos que permanecen vacíos por evidencia insuficiente
- `Ofertas.monto_ofertado_clp`: la respuesta da `monto_total` pero **no acredita moneda de cada cotización**; la moneda del presupuesto del proceso no se usa para deducirla.
- `Resultados.adjudicatario`, `monto_adjudicado_clp` y `fecha_resultado`: la selección informada por API no acredita adjudicación jurídica ni fecha/monto adjudicado. No inventar estos valores.
- Otros campos no provistos oficialmente permanecen vacíos; se distingue **no disponible** de **error de transformación**.

La integración diaria sigue programada a las 22:30 de Chile, con máximo diez consultas nuevas/de seguimiento, sin participar Ubuntu.
