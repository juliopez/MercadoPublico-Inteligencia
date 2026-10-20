# Inventario y catálogo de Google Sheets — 2026-10-20

## Directorio central (creado)
- [Plataforma Mercado Público](https://drive.google.com/drive/folders/1R5SDUh5n7XWxMYWWCRyIYqByMrAoPJ-H)
- [01_Historicos_MER](https://drive.google.com/drive/folders/1YC-1MT1QCnAvpKgDACCH-NKnV9caIFyW)
- [02_Operativo_API](https://drive.google.com/drive/folders/1m3feqWXUNtur6v17qvhZ9bQrB38-ruVS)
- [03_Respaldos](https://drive.google.com/drive/folders/1TQAxQUPsDPACmTBhh3HR7OMyCemC8NAZ)
- [04_Revision_y_Obsoletos](https://drive.google.com/drive/folders/1R2g284moDJOeCsVH8Wf-yiQwgGXBX8je)

## Archivos estructurales identificados

| Nombre | ID | Rol | Situación |
|---|---|---|---|
| MER_2026_09 | `1lnMVUZ_pn_HkwEvI90yYz5GOMSYzuX-FbcbMR71-oDA` | Histórico septiembre 2026, MER v2 seis entidades | **Movido a 01_Historicos_MER y renombrado, sin alterar ID ni datos; auditoría aprobada** |
| Observatorio Mercado Público — Base de Datos | `1y81QaPy37APkBwxlYrKyE66_1ECdhL87GyWNitTfHr4` | Producción antigua; dependencia potencial de ETL/front | **No mover, renombrar ni modificar hasta auditar dependencia** |
| Observatorio Mercado Público — Base de Datos (clone) | `1loeK_IM3RXHaR7CqpjUbz-TsNgOKNrV1ejq8aRC6JyE` | Clon histórico de trabajo | Conservar provisionalmente, sin cambios |
| Respaldo MER v2 antes de septiembre | `1Ry19RiKe87KJLUrs7l-oqqtNTZoGzHIlIq_7_ogO4Tw` | Respaldo de septiembre | Conservar hasta decisión de retención |

## Otros archivos identificados (revisión pendiente)
- `1MOLbU8u2Qb6m9D1fmzKmm4oOx_oLk5vfthC-vlsF-4Y`: Órdenes de compra agosto 2026 detalle.
- `1nqgEiRjKDjTrtgTqifpukcjRFWP2eXjISzr-O1PgUTQ`: Compra Ágil agosto 2026 histórico.
- `1mjQCuLD73KlwE5syUdeTICBG2CYlXPKSFnh5ffi_zEI`: Compra Ágil julio 2026 histórico.
- `1yHPhBUNz0c9DerCqXPOoXB6qoenE5gR3CYavLc4gBs4`: staging temporal procesos septiembre.
- `1QN53JXhzZzRN3JuEqDtPE-j7wlGMUZp48n6LZxLAK6Q`: preparación ofertas septiembre.
- Numerosos respaldos del clon y de cargas, identificados por búsquedas de Drive; **no se han borrado**.

## Catálogo de períodos

| Período | Tipo | ID de Google Sheet | Estado |
|---|---|---|---|
| 2026-06 | Histórico | Pendiente de creación | Pendiente |
| 2026-07 | Histórico | Pendiente de creación | Pendiente |
| 2026-08 | Histórico | Pendiente de creación | Pendiente |
| 2026-09 | Histórico | `1lnMVUZ_pn_HkwEvI90yYz5GOMSYzuX-FbcbMR71-oDA` | Cargado y auditado |
| 2026-10 | Operativo (API) | Pendiente de creación | Pendiente |

## Reglas de preservación
1. No eliminar recursos por su nombre aparente: confirmar identificador, rol, dependencias y respaldo.
2. El mes operativo se alimenta por API; solo se convierte en histórico después del cierre y conciliación oficial.
3. Mantener seis entidades MER v2 en cada archivo mensual.
4. No alterar producción, ETL automáticos, JSON público o frontend sin revisión específica.
5. A medida que avance el inventario, actualizar este catálogo y registrar movimientos realizados.
