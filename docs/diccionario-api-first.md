# Diccionario operativo API-first — Observatorio Mercado Público
Fecha: 2026-10-16. **Contrato de compatibilidad; sin migración ni importación.**

## Regla
Solo son atributos de negocio admisibles los expuestos por los endpoints que consume el ETL (V1 licitaciones/listado+detalle y V2 Compra Ágil/listado+detalle), previa constatación de su significado. Los CSV 2024–2026 se transformarán a este esquema, nunca al contrario. Los campos operacionales privados (fuente, fecha de sincronización, estado de verificación y claves de deduplicación) no son atributos de ChileCompra. «Vacío» significa *no disponible*, no cero.

## Procesos — columnas existentes, sin eliminar antes de validar
| Campo | Procedencia actual | Decisión |
|---|---|---|
| codigo | V1 CodigoExterno; V2 codigo | Conservar, clave |
| nombre | V1 Nombre; V2 nombre | Conservar |
| estado | V1 Estado/CodigoEstado; V2 estado.glosa | Conservar; fuente distinta |
| convocatoria | V2 convocatoria.descripcion | Conservar opcional |
| fecha_publicacion | V1 FechaPublicacion o fecha de consulta del listado; V2 fechas.fecha_publicacion | Conservar, documentar fallback |
| fecha_cierre | V1 FechaCierre/Fechas.FechaCierre; V2 fechas.fecha_cierre | Conservar opcional |
| fecha_ultimo_cambio | V2 fechas.fecha_ultimo_cambio | Conservar opcional; NUNCA cargar fecha de adjudicación V1 aquí |
| monto_disponible_clp | V2 montos.monto_disponible_clp; V1 MontoEstimado | Conservar solo si moneda y definición son comparables; no inferir CLP de monto sin divisa |
| organismo_comprador | V1 Comprador.NombreOrganismo; V2 institucion.organismo_comprador | Conservar |
| rut_organismo | V1 Comprador.RutUnidad; V2 institucion.rut | Privado; verificar si identifica unidad vs organismo |
| unidad_compra | V1 Comprador.NombreUnidad; V2 institucion.unidad_compra | Conservar opcional |
| region | V1 Comprador.RegionUnidad; V2 institucion.nombre_region | Conservar opcional |
| total_ofertas_recibidas | V2 resumen.total_ofertas_recibidas | Conservar; no completar con número de ofertas disponibles |
| motivo_seleccion | V2 motivos.motivo_seleccion | Conservar opcional |
| url_detalle | V2 links.detalle; V1 sin URL equivalente asegurada | Conservar solo enlace oficial comprobado; no sustituir por acta de adjudicación |
| fecha_sincronizacion | Interno | Conservar privado |
| categoria, subcategoria | Clasificaciones locales `Sin clasificar`; NO demostradas en payload actual | Solo clasificación interna claramente identificada; nunca presentarla como dato API oficial |
| codigo_categoria_oficial | No se ha demostrado asignación por el ETL | Dejar sin rellenar o retirar tras auditoría |
| modalidad | Derivada de endpoint consultado | Conservar interno de origen |

## Ofertas — datos públicos comprobables actualmente solo para detalle V2 Compra Ágil
| Campo | API V2 / uso | Decisión |
|---|---|---|
| codigo | Payload codigo | Conservar |
| convocatoria | No se asigna por ETL detalle | Opcional sin inferencias |
| rut_proveedor | proveedores_cotizando.rut_proveedor | Privado |
| proveedor | razon_social | Conservar |
| monto_ofertado_clp | monto_total | Conservar, comprobar moneda |
| moneda | ETL pone `CLP` constante | Corregir si fuente no asegura moneda |
| fecha_oferta | fecha_creacion | Conservar |
| estado_oferta, estado_api | estado | Revisar duplicación semántica; no eliminar hasta adaptar consumidores |
| fuente, fecha_extraccion | Internos | Conservar privado |
| id_cotizacion | id_cotizacion | Conservar, clave junto a codigo |
| valor_neto_clp, impuestos_clp, despacho_clp | valor_neto, total_impuesto, monto_despacho | Conservar si los importes están efectivamente en CLP |
| seleccionado | proveedor_seleccionado | Conservar; no equivale a OC |
| id_oc_interno | id_oc | Conservar privado; NO código de OC pública comprobado |

## Resultados — distinguir selección de adjudicación y contrato
| Campo | Procedencia | Decisión |
|---|---|---|
| codigo | Código proceso | Conservar |
| convocatoria | Actualmente vacío | Evaluar retirada solo tras adaptar ETL |
| rut_adjudicatario, adjudicatario, monto_adjudicado_clp, fecha_resultado | ETL Compra Ágil NO los rellena | Solo poblar mediante respuesta API que verifique la adjudicación |
| motivo_seleccion | V2 motivos.motivo_seleccion | Conservar opcional |
| fuente, validado, estado_verificacion_oc, fecha_extraccion | Metadatos internos | Conservar privado salvo indicador público de verificación |
| id_cotizacion_ganadora, monto_oferta_seleccionada_clp, id_oc_interno | V2 oferta seleccionada | Conservar, diferenciados de adjudicación contractual |
| tipo_resultado, clave_resultado | Clasificación y clave técnicas propuestas | Condicionales a migración validada; claves solo basadas en IDs reales |
| fuente_adjudicacion, codigo_oc_publica, url_documento_publico, id_linea_adjudicacion | NO demostrados de extremo a extremo en API actual | No crear ni rellenar durante migración hasta verificar endpoint y semántica |

## Bloqueos que deben resolverse ANTES de producción
1. **Licitaciones:** ETL de detalle actualmente enriquece Procesos pero NO escribe Ofertas ni Resultados. No declarar validadas esas dos extracciones.
2. **Compra Ágil:** `DETAIL_MAX_CODES` aún está restringido a 1–100 con valor predeterminado 10 en ETL de detalle. La operación diaria no debe adoptar ese máximo de piloto; resolver paginación/lotes sin omitir procesos.
3. **Publicación:** el workflow integral exporta todos los datos presentes en Sheets, no solo los diez procesos sometidos a validación; la validación no equivale a muestra pública de diez.
4. **Alcance CSV:** los CSV de Compra Ágil pueden carecer de `id_cotizacion`. No inventar claves; importar menos ofertas si no hay identificador fiable.
5. **Recuperación:** registro persistente por fecha+modalidad+componente aún no conectado a automatización diaria; reintentos actuales no equivalen a recuperación automática de jornadas anteriores.
6. **Control de capacidad:** los máximos 10.000 Procesos, 20.000 Ofertas y 10.000 Resultados son techos provisionales; pueden reducirse. Verificar celdas, latencia, integridad y tamaño del JSON antes de producción.
7. **No eliminar columnas hasta respaldo, revisión del frontend y validación de una migración reversible.**

## Criterio de aceptación
La prueba integral está aprobada solo cuando se verifica lectura API → escritura Sheets → integridad/idempotencia → exportación JSON → sitio publicado, con cualquier cobertura ausente explícitamente documentada. Una consulta HTTP 504 o una ejecución en cola no es aprobación. Históricos: ninguna importación hasta aprobación posterior.
