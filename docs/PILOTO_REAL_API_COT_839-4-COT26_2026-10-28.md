# Fase 2 — Primera carga real supervisada de un proceso Compra Ágil
**Fecha de ejecución local:** 28 de octubre de 2026 (artefacto GitHub UTC 29/10). **Proceso:** `839-4-COT26`. **Estado:** PILOTO EN COPIA SHEETS APROBADO; NO PRODUCCIÓN.

## Evidencia
- **Única consulta real:** GitHub Actions [run 40793647741](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/40793647741). Paso de consulta y cifrado correcto; ejecución general success. Script `scripts/captura_cifrada_piloto_api_mer.py` y workflow `.github/workflows/piloto-unico-api-cifrado.yml` (disparador por incorporación de workflow; no programación recurrente).
- Endpoint consultado: `https://api2.mercadopublico.cl/v2/compra-agil/839-4-COT26`; autenticación desde secreto GitHub `CHILECOMPRA_TICKET`. HTTP 200. JSON: `success="OK"`; `payload.codigo="839-4-COT26"`; 15 cotizaciones; 1 seleccionada.
- Respuesta íntegra cifrada AES-256-GCM + RSA-OAEP SHA-256; artifact `mer-api-piloto-839-4-COT26-cifrado`, ID `12863140854`, expiración indicada 2026-11-05T00:23:10Z. El archivo original se recuperó y descifró en un entorno privado. **Nunca se incorporó JSON original ni clave privada a GitHub**.
- SHA256 JSON original: `9836161ea057a1e874fc8d179482d98ea6c15f59f54f062428d003e843e68f5a`.
- Los `fecha_creacion` de las 15 cotizaciones van del **14 al 22 de julio 2026**, por tanto **NO usar este ejemplo como registro de octubre**. Su propósito es validar el mecanismo técnico para luego escoger procesos de octubre.

## Escritura real y verificación
- **Copia de prueba**: https://docs.google.com/spreadsheets/d/18iPCaHbNTpjIfgMsNu3ZhQ0u9lBqx4_zaDdWgrSkcqY/edit, distinta del MER operativo `1v12ztJfxvltzv1rJQBsxxmyMwmnuc2DUx87SeRCSnz4`.
- Inserción mediante **conector de Google Sheets de ChatGPT**, con una operación Sheets `batchUpdate` que añadió **15 filas a Ofertas** y **1 fila a Resultados**.
- Relectura posterior `Ofertas!A1:I25`, `Resultados!A1:J10`: 15 cotizaciones para código, 15 IDs únicos, una `seleccionado=1`; 1 resultado cuyo `id_cotizacion_ganadora` coincide con esa oferta. No había registros previos de ese código en la copia en el momento de insertar. Sí había dos filas sintéticas previas no relacionadas; se conservaron sin modificación.
- `monto_ofertado_clp`, `monto_adjudicado_clp` y `monto_oferta_seleccionada_clp` quedaron vacíos: **no se certificó moneda**. `id_proveedor` vacío para conciliación posterior; RUT de cotizante permanece solo en tabla privada `Ofertas`, no se exportó. `validado="No: selección API; adjudicación no verificada"`.
- No se consultaron otros procesos; sin escritura en MER operativo; sin cron alterado; sin despliegue Pages.

## Estado al cierre del piloto
**Aprobado:** respuesta única conservada, transformación real, 15+1 filas en copia privada, deduplicación observada por claves, integridad de selección. **Pendiente antes de carga de octubre:** elegir procesos realmente correspondientes a octubre, determinar criterio de periodo y moneda; conciliar `id_proveedor`, activar actualización masiva idempotente sobre MER operativo con resguardo y extender exportador vigente a Ofertas/Resultados, sin revalidar cron ni índices generales ya probados. La escritura de este caso fue hecha por conector, no demuestra ejecución con identidad de servicio en Actions.

**Seguridad:** el artifact cifrado tiene retención de 7 días; la clave privada se generó fuera del repositorio. Guardar respaldos privados de forma duradera antes de depender del artifact. No anexar nunca JSON original con RUT ni clave privada a este documento ni a commits.
