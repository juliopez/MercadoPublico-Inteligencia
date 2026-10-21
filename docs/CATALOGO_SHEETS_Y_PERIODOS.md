# Inventario y catálogo de Google Sheets — 2026-10-20

## Directorio central (creado)
- [Plataforma Mercado Público](https://drive.google.com/drive/folders/1R5SDUh5n7XWxMYWWCRyIYqByMrAoPJ-H)
- [01_Historicos_MER](https://drive.google.com/drive/folders/1YC-1MT1QCnAvpKgDACCH-NKnV9caIFyW)
- [02_Operativo_MER](https://drive.google.com/drive/folders/1m3feqWXUNtur6v17qvhZ9bQrB38-ruVS)
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
| 2026-06 | Histórico | `137pknbQIBbm5WAYvFh5bXKTGX9uBVhBYleTwxO6x7PI` | 798.094 registros; auditoría estructural/referencial aprobada con observaciones |
| 2026-07 | Histórico | `1LcVUrWn99deDkgphD8cAn2n4jLxl-HZyzNm0XGffC5w` | 810.333 registros; auditoría estructural/referencial aprobada con observaciones |
| 2026-08 | Histórico | `1TY41r2eriz3wvvLvHdYxHVrbqk94Lsp1kFtDtxxcXEs` | 834.370 registros; auditoría independiente aprobada con observaciones (20-10-2026) |
| 2026-09 | Histórico | `1lnMVUZ_pn_HkwEvI90yYz5GOMSYzuX-FbcbMR71-oDA` | Cargado y auditado |
| 2026-10 | Operativo (API) | `1v12ztJfxvltzv1rJQBsxxmyMwmnuc2DUx87SeRCSnz4` | Creado, seis tablas MER v2 vacías; integración API pendiente |

## Reglas de preservación
1. No eliminar recursos por su nombre aparente: confirmar identificador, rol, dependencias y respaldo.
2. El mes operativo se alimenta por API; solo se convierte en histórico después del cierre y conciliación oficial.
3. Mantener seis entidades MER v2 en cada archivo mensual.
4. No alterar producción, ETL automáticos, JSON público o frontend sin revisión específica.
5. A medida que avance el inventario, actualizar este catálogo y registrar movimientos realizados.

## Segunda etapa ejecutada — 20 de octubre de 2026

- Creados y verificados en `01_Historicos_MER`: [MER_2026_06](https://docs.google.com/spreadsheets/d/137pknbQIBbm5WAYvFh5bXKTGX9uBVhBYleTwxO6x7PI/edit), [MER_2026_07](https://docs.google.com/spreadsheets/d/1LcVUrWn99deDkgphD8cAn2n4jLxl-HZyzNm0XGffC5w/edit) y [MER_2026_08](https://docs.google.com/spreadsheets/d/1TY41r2eriz3wvvLvHdYxHVrbqk94Lsp1kFtDtxxcXEs/edit).
- Cada una contiene las seis pestañas con encabezados del contrato MER v2: `Procesos`, `Proveedores`, `Ofertas`, `OrdenesCompra`, `VinculosCOT_OC` y `Resultados`. No se incorporaron históricos ni se modificaron otras bases.
- Copias antiguas de trabajo, staging y respaldos siguen identificadas para revisión de dependencias; no se eliminaron ni trasladaron preventivamente.

## Tercera etapa — 20 de octubre de 2026

- [MER_2026_10_OPERATIVO](https://docs.google.com/spreadsheets/d/1v12ztJfxvltzv1rJQBsxxmyMwmnuc2DUx87SeRCSnz4/edit) creado y ubicado en [02_Operativo_MER](https://drive.google.com/drive/folders/1m3feqWXUNtur6v17qvhZ9bQrB38-ruVS), con las seis pestañas MER v2 y encabezados idénticos al histórico. **Sin registros; sin integración API activada**.
- Archivos adicionales identificados para revisión, no eliminar: `149_YB64BfW22rKnfAkrNxrUB8dQVV4GS3YK7lGIs1Z8` (Compra Ágil septiembre preparada), `1In5DsxX5BB1Z20U7tQi0WbXXybrE3lNuK8K1y-z0AUM` (respaldo Indicadores), `14HSCjPvPCJJtAhf9Mi8t59TiGI4FzEpo_zxBbVSVzYU` (respaldo Control), `13CUdwUHkFXN_gmOCv3q4tNrCq-4FBn5_bvhYgaRXgx0` (respaldo Resultados), `1h32aq-keyo_Qg-QWUqbBSLNtDSJHiAuyJqMaNQcBKgo` (respaldo Ofertas).
- Archivos originales de producción, clon y respaldos no se borraron ni movieron. El inventario completo de dependencias sigue en curso.

## Carga agosto verificada — 20 de octubre de 2026

Consulta directa de MER_2026_08: dimensiones exactas esperadas y última fila con datos en cada pestaña. Procesos 83.937, Proveedores 30.564, Ofertas 432.111, OrdenesCompra 153.221, VinculosCOT_OC 68.592, Resultados 65.945; total 834.370. **Verificación de final de carga por totales y filas; auditoría independiente PK/FK pendiente.** No repetir la carga. Siguiente período a preparar: julio 2026.

## Auditoría posterior a agosto — herramienta lista

Notebook de auditoría MER v2 [generalizado por período](https://colab.research.google.com/github/juliopez/MercadoPublico-Inteligencia/blob/main/colab/Auditoria_Integridad_MER_v2_Colab.ipynb), por defecto `PERIODO='2026-08'`, destino restringido a `MER_2026_08`. Conteos esperados agosto: Procesos 83.937; Proveedores 30.564; Ofertas 432.111; OrdenesCompra 153.221; VinculosCOT_OC 68.592; Resultados 65.945. La auditoría es **solo lectura** y produce `auditoria_integridad_mer_v2_2026-08.json`. **Pendiente de ejecución y recepción de informe**, por lo tanto agosto aún no está cerrado formalmente.

## Cierre estructural de agosto — 2026-10-20

Evidencia: `auditoria_integridad_mer_v2_2026-08.json` generado 2026-10-20T21:51:20Z sobre `MER_2026_08` (solo lectura). Estado: `AUDITORIA_COMPLETADA_CON_OBSERVACIONES`. Procesos 83.937, Proveedores 30.564, Ofertas 432.111, OrdenesCompra 153.221, VinculosCOT_OC 68.592, Resultados 65.945; **total 834.370**. PK vacías 0, duplicadas 0, campos extra/ausentes 0 en todas las tablas. FK auditadas sin huérfanos; 0 pares COT–OC duplicados. **Observaciones**: 24.097 vínculos OC fuera del corte (aceptados por cobertura), 65.945 resultados `OC no verificada`, proveedores `RUT_SIN_CONTRASTE` 30.516 y `SIN_RUT` 48. Cierre de integridad estructural/referencial **aprobado**, sin certificar adjudicaciones jurídicas ni identidades tributarias. Siguiente período julio 2026.

## Julio 2026 — carga verificada

Colab informó `CARGA MER V2 FINALIZADA 2026-07`. Se verificaron dimensiones de las seis pestañas en Google Sheets (80.996 Procesos, 29.827 Proveedores, 437.855 Ofertas, 150.980 OrdenesCompra, 56.149 VinculosCOT_OC y 54.526 Resultados; 810.333 registros). La **auditoría referencial posterior** aún está pendiente. No repetir la carga.

## Cierre estructural de julio — 2026-10-20

Evidencia: `auditoria_integridad_mer_v2_2026-07.json`, 2026-10-20T23:04:32Z, MER v2 julio, solo lectura. Estado: `AUDITORIA_COMPLETADA_CON_OBSERVACIONES`. Procesos 80.996, Proveedores 29.827, Ofertas 437.855, OrdenesCompra 150.980, VinculosCOT_OC 56.149, Resultados 54.526; total **810.333**. Cero claves primarias vacías o duplicadas, cero columnas extra o ausentes; referencias auditadas sin huérfanos, cero pares COT–OC repetidos. Observaciones: 14.080 vínculos con OC fuera del corte (cobertura aceptada), 54.526 resultados OC no verificada, 29.762 proveedores RUT sin contraste y 65 SIN_RUT. **Cierre estructural aprobado;** no es certificación jurídica. Siguiente período: junio 2026.

## Junio 2026 — carga verificada

Colab informó `CARGA MER V2 FINALIZADA 2026-06`. Verificación directa de dimensiones y presencia de datos en las últimas filas de MER_2026_06: Procesos 80.898, Proveedores 29.741, Ofertas 407.923, OrdenesCompra 150.451, VinculosCOT_OC 65.867, Resultados 63.214; total **798.094**. Queda pendiente **auditoría independiente estructural/referencial**, antes de marcar la tarea 7 completa. No volver a insertar el paquete de junio.

## Cierre estructural de junio — 2026-10-20

Evidencia: `auditoria_integridad_mer_v2_2026-06.json` generado 2026-10-21T00:06:46Z sobre `MER_2026_06`, en modo solo lectura. Estado: `AUDITORIA_COMPLETADA_CON_OBSERVACIONES`.

| Tabla | Registros | PK vacías | PK duplicadas |
|---|---:|---:|---:|
| Procesos | 80.898 | 0 | 0 |
| Proveedores | 29.741 | 0 | 0 |
| Ofertas | 407.923 | 0 | 0 |
| OrdenesCompra | 150.451 | 0 | 0 |
| VinculosCOT_OC | 65.867 | 0 | 0 |
| Resultados | 63.214 | 0 | 0 |
| **Total** | **798.094** | **0** | **0** |

Todas las tablas: cero campos extra/ausentes; integridad referencial evaluada sin huérfanos; cero pares COT–OC repetidos. Observaciones aceptadas: 21.634 vínculos OC fuera del corte; 63.214 resultados `OC no verificada`; 29.698 proveedores `RUT_SIN_CONTRASTE` y 43 `SIN_RUT`. **Junio queda cerrado en integridad estructural y referencial**, sin acreditar adjudicaciones ni identidades tributarias.

### Fin de carga histórica extraordinaria

Los cuatro períodos previstos **2026-06, 2026-07, 2026-08 y 2026-09** están cargados en cuatro Google Sheets separados y cuentan con auditoría estructural/referencial independiente aprobada con observaciones. El alcance de esta carga extraordinaria termina en junio; no se incorporarán más meses históricos anteriores sin un nuevo acuerdo.

## Inventario consolidado y organización — octubre 2026

**Registro de lectura automática:** [`config/catalogo_sheets.json`](../config/catalogo_sheets.json), fuente de referencia de los cinco períodos, carpetas y exclusiones. La nomenclatura operativa es `MER_AAAA_MM_OPERATIVO` y la histórica `MER_AAAA_MM`.

**Verificación de carpetas:** `01_Historicos_MER` contiene cuatro documentos (junio–septiembre); `02_Operativo_MER` contiene octubre. Cuatro respaldos MER v2 (uno por mes cargado) fueron movidos a `03_Respaldos`. También se organizaron respaldos previos del clon y producción identificados por nombre. Los archivos auxiliares de Compra Ágil, OC y staging pasaron a `04_Revision_y_Obsoletos` **sin borrarlos**. Los movimientos conservaron los ID de Google Drive.

**Archivos críticos excluidos de movimientos y depuración:** producción antigua `1y81QaPy37APkBwxlYrKyE66_1ECdhL87GyWNitTfHr4` y clon histórico `1loeK_IM3RXHaR7CqpjUbz-TsNgOKNrV1ejq8aRC6JyE`. Deben mantenerse disponibles hasta comprobar dependencias de ETL y publicación vigente.

**Depuración pendiente:** la carpeta de revisión no significa que sus contenidos puedan eliminarse. Identificar dependencias, verificar respaldo y presentar una lista exacta de ID para autorización explícita antes de enviar a papelera. Los respaldos se conservan por precaución. El inventario abarca los recursos identificados en búsquedas del proyecto, no certifica una enumeración exhaustiva de cualquier archivo cuyo nombre no aluda al proyecto.

## Preparación del cambio octubre–noviembre 2026

- Creada [MER_2026_11_OPERATIVO](https://docs.google.com/spreadsheets/d/1faLUhyB13Qty7dSNqbRHLCmpq-cxgW8bIOgPN0KCWnE/edit) en `02_Operativo_MER` (ID `1faLUhyB13Qty7dSNqbRHLCmpq-cxgW8bIOgPN0KCWnE`). Seis pestañas MER v2 y encabezados del contrato; sin registros.
- Cuenta de servicio GCP con permiso de edición compartido; **no se ha probado desde Ubuntu la conexión con esta hoja nueva**.
- Catálogo `config/catalogo_sheets.json` incorpora `2026-11` como `operativo`. Al cambiar fecha local a noviembre, `ubuntu_cron_etl.sh` selecciona automáticamente noviembre. Octubre conserva su ID y registros y **no se renombra ni archiva automáticamente**.
- Limitación estructural: las cuentas de servicio usadas en Ubuntu no pueden crear libremente nuevas hojas en My Drive por cuota de almacenamiento (`storageQuotaExceeded`). Se aprovisionó noviembre desde la conexión de Google Drive autorizada por el usuario. Para diciembre y posteriores se requiere preaprovisionar/registrar la nueva hoja o implementar un método OAuth autorizado; el bloqueo mensual impide cargar en una hoja errónea.
