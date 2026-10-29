# Fase 2 — Primera carga real controlada en MER operativo, octubre 2026
**Fecha local de operación:** 28/10/2026 (ejecuciones GitHub UTC 29/10). **Estado:** PRIMER LOTE ESCRITO Y VERIFICADO. **Ámbito:** solo Ofertas y Resultados.

## Libro operativo y respaldo
- MER octubre oficial: https://docs.google.com/spreadsheets/d/1v12ztJfxvltzv1rJQBsxxmyMwmnuc2DUx87SeRCSnz4/edit
- Respaldo previo independiente, creado en carpeta oficial de respaldos: https://docs.google.com/spreadsheets/d/1z5L-ed-At0q8LANiGpama1Dldx27dbA_m4X-7lhAiok/edit
- Se verificó que ambos libros tienen las seis pestañas originales. No se modificaron otras pestañas, el cron o el portal público.

## Hallazgo fundamental del origen
- `Procesos` del MER octubre contiene 3.509 filas de licitaciones, **ningún proceso `COT26`**; `Ofertas` y `Resultados` estaban vacías.
- `VinculosCOT_OC` contiene 2.676 vínculos con **2.669 códigos COT únicos**, pero **no** demuestra pertenencia al mes de octubre: tres códigos inicialmente seleccionados desde los vínculos se publicaron realmente en julio. Se consultaron y guardaron cifrados pero NO se escribieron en octubre.
- Consulta API V2 de listado por `publicado_desde/publicado_hasta` para 27/10 devolvió 5.695 procesos, primera página 10 registros sin ofertas.
- Consulta por fecha 01/10 sin filtro devolvió 4.402 procesos y primera página de 10, varios con proveedor seleccionado. Una consulta con filtro de estado `proveedor_seleccionado` devolvió cero, por lo cual no se debe confiar en ese filtro sin investigar su semántica.
- Fuente del listado y detalles: endpoint V2 de Compra Ágil con ticket desde secreto GitHub, respaldos originales cifrados. No publicar RUT ni respuestas originales en GitHub.

## Primer lote real incorporado al MER operativo
**Criterio:** `payload.fechas.fecha_publicacion` del detalle oficial debe pertenecer a octubre.

| Código COT | Fecha publicación oficial | Ofertas | Seleccionadas | Resultados |
| --- | --- | ---: | ---: | ---: |
| `3853-565-COT26` | 2026-10-01 23:29 | 4 | 1 | 1 |
| `5668-58-COT26` | 2026-10-01 23:22 | 6 | 1 | 1 |
| `607603-61-COT26` | 2026-10-01 23:10 | 8 | 1 | 1 |
| **Total** | | **18** | **3** | **3** |

- GitHub Actions [run 40797109349](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/40797109349): capturó exactamente tres detalles y preservó respuestas originales en artifact cifrado `mer-api-lote3-octubre-1-cifrado`.
- Escritura realizada por conector Google Sheets con **una sola operación batchUpdate de dos appendCells**: 18 filas `Ofertas`, 3 filas `Resultados`.
- Relectura independiente de `Ofertas!A1:I28` y `Resultados!A1:J12`: se confirmaron 18 ofertas, 3 resultados, 18 claves `(codigo,id_cotizacion)` diferentes, una seleccionada por proceso y correspondencia exacta entre resultado y cotización seleccionada.
- Los montos `*_clp` se dejaron vacíos hasta certificar moneda. `id_proveedor` vacío hasta resolverlo por RUT mediante Proveedores sin duplicar identidades; el RUT original queda en tabla privada Ofertas. `validado` indica expresamente **selección API, adjudicación no verificada**.
- La consulta es finita y controlada: este ensayo **no** habilitó el workflow diario 22:30 ni retroalimentó automáticamente la cola.

## Pendientes críticos antes de publicar/masificar
1. La ausencia de Compra Ágil en `Procesos` causa potenciales filas huérfanas para el frontend; hay que integrar los procesos del mes por la vía que corresponde a esa entidad, **sin utilizar la API para duplicar campos existentes de fuentes ETL ni reemplazar el cron**. Validar contrato/periodo.
2. Confirmar la moneda de `monto_total`, consolidar `id_proveedor` con datos internos y diferenciar formalmente selección de adjudicación y relación OC.
3. Implementar checkpoints persistentes y consulta incremental acotada, partiendo de estos códigos ya procesados; nunca reconsultarlos a ciegas.
4. Ampliar la exportación operativa de Ofertas/Resultados y reutilizar los índices y publicación existentes; pruebas controladas antes de activar 22:30.
5. El trabajo experimental de captura y ensayos sigue en rama `etapa2/escritor-prueba-20261028` y PR #1; no fusionar indiscriminadamente workflows de consulta de un solo uso a main. **Esta documentación del lote oficial sí quedó en main**.

## Seguridad / disponibilidad
Los artefactos cifrados de GitHub Actions tienen retención breve (7 días). La copia de trabajo de JSON originales se guarda fuera del repositorio y no debe divulgarse; el reuso duradero requiere un almacén privado autorizado.
