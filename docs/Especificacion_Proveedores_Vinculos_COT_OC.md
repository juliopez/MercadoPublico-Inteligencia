# Especificación lógica — entidades nuevas del MER

**Estado:** diseño propuesto, sin migración ejecutada. **Ámbito:** Google Sheets clon, carga histórica manual y futuras conciliaciones. No modificar producción, ETL automáticos ni frontend sin una fase separada de validación.

## PROVEEDORES

| Atributo | Tipo lógico | Restricción | Uso |
| --- | --- | --- | --- |
| `id_proveedor` | texto | **PK**, obligatorio | Identificador interno estable, no depende del nombre |
| `rut_canonico` | texto | único si informado y validado; admite vacío | RUT normalizado, conservando dígito verificador |
| `razon_social_canonica` | texto | puede faltar | Denominación preferente, **no** clave |
| `nombre_fantasia` | texto | opcional | Identificación comercial |
| `fuente_principal` | texto | obligatorio al registrar | Procedencia del dato |
| `estado_identidad` | texto | obligatorio | `RUT_CONCORDANTE_FUENTES`, `RUT_SIN_CONTRASTE`, `SIN_RUT`, `CONFLICTO_RUT` |

**Criterios de identidad:**
- El RUT del histórico COT (`RUTProveedor`) y el campo de OC (`RutSucursal`) **se conservan separadamente en sus entidades**: su coincidencia es un contraste entre fuentes, no prueba externa de titularidad.
- `CodigoProveedor` de OC es identificador interno de ChileCompra: jamás convertirlo a RUT. `codigo_proveedor_oc` se conserva en `ORDENES_COMPRA`.
- No consolidar automáticamente identidades por igualdad o similitud de razón social. Un registro sin RUT confiable no debe absorber otro basado exclusivamente en el nombre.
- Generar `id_proveedor` determinísticamente desde RUT normalizado cuando exista; en casos sin RUT, asignar un ID propio y persistente con trazabilidad de fuente. **No cambiar una PK al descubrir datos nuevos**; las reconciliaciones se registran y aprueban antes de actualizar FKs.
- La unicidad condicional de `rut_canonico` se aplica mediante validaciones del importador/auditoría: Google Sheets no aplica índices UNIQUE nativos.

## VINCULOS_COT_OC

| Atributo | Tipo lógico | Restricción | Uso |
| --- | --- | --- | --- |
| `id_vinculo` | texto | **PK**, obligatorio | ID técnico reproducible |
| `codigo_cot` | texto | **FK** a `PROCESOS.codigo`, obligatorio | Cotización Compra Ágil |
| `codigo_oc` | texto | **FK** a `ORDENES_COMPRA.codigo_oc` si la OC está cargada | Referencia oficial `CodigoOC` del histórico COT |
| `origen_vinculo` | texto | obligatorio | Archivo/mes y campo de origen |
| `estado_oc_historico` | texto | opcional | Estado tal como figura en COT |
| `fecha_aceptacion_oc` | fecha/texto | opcional | Fecha si la fuente la informa |
| `relacion_confiable` | texto | obligatorio | `CODIGO_OC_OFICIAL`, `NO_VERIFICADO`, `CONFLICTO` |

**Regla fundamental:** una COT puede tener múltiples OC. Deducir `id_vinculo` de par normalizado (`codigo_cot`, `codigo_oc`) y exigir unicidad de ese par para los vínculos oficiales, sin eliminar información sobre eventos históricos; si se requieren versiones, diseñar una tabla/eventos aparte antes de alterar la PK.

**FK diferida:** la referencia a una OC de otro período puede no estar presente en `OrdenesCompra` del clon. Se almacena **el código oficial de OC** en el vínculo, con validación referencial `PENDIENTE_POR_CORTE`; no descartarlo, no forzar OC ficticias ni cargar otros meses para resolverlo. Por tanto, `codigo_oc` es **referencia lógica a OC, que puede estar ausente localmente**, no FK físicamente exigible en la carga mensual. Lo mismo aplica a posteriores importaciones que no cubran la COT correspondiente.

## Compatibilidad y plan de migración

1. Congelar y respaldar las cabeceras actuales y las cantidades verificadas de `Procesos` (83.937), `Ofertas` (432.111), `Resultados` (65.945), `OrdenesCompra` (153.220) para el corte auditado de agosto.
2. Crear **solo en el clon**, en una fase posterior autorizada, las pestañas `Proveedores` y `VinculosCOT_OC` con los encabezados de esta especificación.
3. Poblar proveedores desde identificadores oficiales conservados en los históricos; generar un reporte de conflictos y consolidaciones; **no escribir FKs huérfanas**.
4. Poblar vínculos del archivo de relaciones COT–OC respaldado (68.093 vínculos en agosto) conservando asociaciones fuera de corte sin clasificarlas como errores.
5. Evaluar en una fase separada columnas FK opcionales en `Ofertas` y `OrdenesCompra`. No modificar columnas/orden existentes sin auditoría del contrato Front–Sheets–ETL.
6. Auditar nuevamente unicidad, integridad, conteos, claves desconocidas y compatibilidad de JSON/front antes de proponer promoción a producción.

**Limitación del MER:** un diagrama ER conceptual no impone directamente claves foráneas en Google Sheets. Las referencias a entidades de otro período son opcionales en la cobertura local; las reglas de validación deben implementarse explícitamente en scripts y no debe confundirse integridad estructural con verificación jurídica.
