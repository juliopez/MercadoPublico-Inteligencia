# Contrato de datos · Observatorio Mercado Público · V1 (2026)

**Ámbito:** todos los rubros. **Horizonte:** procesos de 2026. **Fuente:** ChileCompra. **Carga masiva:** posterior. **Programación:** manual hasta validación final.

## Tablas operativas
Las hojas existentes son tablas lógicas relacionadas. Las cabeceras siguientes son el objetivo del modelo y deben respetar este orden.

### Procesos (clave: codigo)
`codigo`, `nombre`, `estado`, `convocatoria`, `fecha_publicacion`, `fecha_cierre`, `fecha_ultimo_cambio`, `monto_disponible_clp`, `organismo_comprador`, `rut_organismo`, `unidad_compra`, `region`, `total_ofertas_recibidas`, `motivo_seleccion`, `url_detalle`, `fecha_sincronizacion`, `categoria`, `subcategoria`, `codigo_categoria_oficial`, `modalidad`.

### Ofertas (clave: id_cotizacion; FK: codigo)
`codigo`, `convocatoria`, `rut_proveedor`, `proveedor`, `monto_ofertado_clp`, `moneda`, `fecha_oferta`, `estado_oferta`, `fuente`, `fecha_extraccion`, `id_cotizacion`, `valor_neto_clp`, `impuestos_clp`, `despacho_clp`, `seleccionado`, `id_oc_interno`, `estado_api`.

### Resultados (clave: codigo; FK: codigo)
`codigo`, `convocatoria`, `rut_adjudicatario`, `adjudicatario`, `monto_adjudicado_clp`, `fecha_resultado`, `motivo_seleccion`, `fuente`, `validado`, `id_cotizacion_ganadora`, `monto_oferta_seleccionada_clp`, `id_oc_interno`, `estado_verificacion_oc`, `fecha_extraccion`.

### Control
A:B conserva metadatos operativos. D:K registra histórico de ejecución (`fecha_utc`, `codigo`, `http_resultado`, `estado_extraccion`, `ofertas_recuperadas`, `ofertas_insertadas`, `ofertas_actualizadas`, `observacion`).

## Semántica y reglas
- `monto_disponible_clp` = presupuesto, **no monto adjudicado**.
- `monto_ofertado_clp` = valor de oferta; `seleccionado` = selección del comprador, **no contrato verificado**.
- `monto_adjudicado_clp` y `adjudicatario` permanecen vacíos hasta verificar orden de compra/acto contractual.
- `categoria` y `subcategoria`: `Sin clasificar` si la fuente no permite asignación comprobable; `codigo_categoria_oficial` vacío si no existe.
- `modalidad` distingue Compra Ágil de licitaciones; órdenes de compra representan documentos de contratación, no categorías temáticas.
- `codigo` es único en Procesos y Resultados; `id_cotizacion` es único en Ofertas. Una oferta pertenece a un proceso; un resultado verificado puede apuntar a una oferta seleccionada.
- Montos numéricos en CLP y fechas ISO cuando estén disponibles; mantener valor bruto cuando no exista una transformación validada.
- V1 consume CSV de las tablas, sin exponer credenciales de Google o ChileCompra en frontend público.

## Estado de implementación
- El contrato lógico está definido.
- La hoja **Procesos** debe completar/verificar `P1=fecha_sincronizacion` y `T1=modalidad`; en última inspección estaban vacías. No se presupone una migración completada.
- El adaptador V1 de licitaciones todavía **no** fue validado mediante ejecución exitosa; no presupone cobertura integral de modalidades.
- El frontend V1 es un explorador de registros; no es un dashboard ni sustituye la base de datos.
