# Ensayo real de Google Sheets — Etapa 2 — 28/10/2026

## Evidencia verificable
- MER operativo fuente, solo copiado: `1v12ztJfxvltzv1rJQBsxxmyMwmnuc2DUx87SeRCSnz4`.
- Libro de ensayo independiente: https://docs.google.com/spreadsheets/d/18iPCaHbNTpjIfgMsNu3ZhQ0u9lBqx4_zaDdWgrSkcqY/edit
- Copia realizada con Drive; se confirmaron 6 pestañas, idénticos sheetId y cabeceras reales de 9 campos (Ofertas) y 10 campos (Resultados).
- Insertada una fila sintética en `Ofertas` mediante Sheets batchUpdate `appendCells`: ID `TEST-API-0001`, proceso `TEST-20261028-COT26`.
- Insertada una fila sintética en `Resultados`: código `TEST-20261028-COT26`, selección `TEST-API-0001`.
- Relectura por separado de `Ofertas!A1:I3` y `Resultados!A1:J3` confirmó ambas filas; los valores `id_proveedor`, RUT y montos quedan vacíos. No se usaron identidades ni adjudicaciones reales.
- No se invocó ChileCompra, no se escribieron datos al MER operativo, ni se publicó el ensayo en GitHub Pages.

## Límites de esta prueba
- La inserción se realizó mediante el conector Google Sheets, **no** ejecutando `scripts/escribir_api_mer_libro_prueba.py` con las credenciales de Ubuntu.
- Por tanto, **no** certifica aún: coincidencia de cuenta de servicio, uso de `MER_API_TEST_SHEET_ID`, candado Ubuntu, respaldo 0600 del escritor, reintento idempotente del escritor, recuperación tras fallo parcial o despliegue en Pages.
- El PR #1 permanece como borrador y su ejecución offline inicial fue exitosa: https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/40790425381.
- La copia es un libro completo de ensayo, no destinado a publicación; revisar y limitar permisos antes de compartir.

## Próximo paso
Ejecutar el escritor Python contra esta copia utilizando exclusivamente una identidad de servicio autorizada, después demostrar segunda ejecución sin duplicados y publicar solo JSON sintéticos de preview aislado, jamás el catálogo operativo.
