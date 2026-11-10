# Observatorio Mercado Público — Continuidad Fase 2 API ↔ MER
**Corte:** 28 de octubre de 2026. **Estado:** desarrollo y ensayos sin carga API real al MER. **Rama:** `etapa2/escritor-prueba-20261028`; [PR #1](https://github.com/juliopez/MercadoPublico-Inteligencia/pull/1) borrador, no fusionado.

## 1. Contexto y objetivo
Repositorio: https://github.com/juliopez/MercadoPublico-Inteligencia

Fase 1 **cerrada** 27/10: cron Ubuntu de lunes a viernes a las 16:00 America/Santiago, ETL de ZIP licitaciones/OC, conciliación COT–OC, Google Sheets MER, exportación de catálogo y derivados GitHub Actions, despliegue GitHub Pages. **No reconstruir ni desactivar la cadena**. La incorporación API complementará las tablas `Ofertas` y `Resultados`, que el flujo operativo de octubre aún no publica con nuevos datos.

MER operativo **2026-10**: `1v12ztJfxvltzv1rJQBsxxmyMwmnuc2DUx87SeRCSnz4` (NO modificar sin autorización específica). Seis pestañas: `Procesos` (16 columnas), `Ofertas` (9), `Resultados` (10), `OrdenesCompra` (13), `Proveedores` (6), `VinculosCOT_OC` (7). No existen `Control` ni `ControlV2` en este libro. Las cabeceras reales están en `docs/AUDITORIA_API_MER_2026-10-28.md`. Total 61 columnas. **No todas las 19 columnas de Ofertas/Resultados provienen de API**: fuentes, validación e ID canónico del proveedor son gestionados por MER.

## 2. Primera prueba de API realizada, sin guardar JSON original
[GitHub Actions run 40787977408](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/40787977408), éxito:
- Compra Ágil V2 detalle `839-4-COT26`: HTTP 200, código válido, 15 cotizaciones; una seleccionada; presentes `id_cotizacion`, `razon_social`, `monto_total`, `fecha_creacion`, `proveedor_seleccionado`, `rut_proveedor`; selección y monto candidato para Resultados.
- Licitación V1 `1000-24-LE26`: HTTP 200 pero no se identificó adjudicación coincidente con la estructura esperada; NO demuestra inexistencia de adjudicación.
- **Advertencia:** la primera prueba sólo guardó conteos/banderas en log; **no se conservó el JSON de las 15 ofertas**. Transformarlas ahora sin nueva consulta no es posible. No se han realizado nuevas llamadas API desde entonces.
- No equiparar cotización seleccionada con adjudicación jurídica, ni inferir moneda CLP sin verificar.

## 3. Componentes implementados
En `main`:
- `scripts/probar_campos_api_mer.py`: sondeo de campos, lectura API.
- `scripts/adaptar_detalle_compra_agil_mer.py`: API V2 → Ofertas(9)/Resultados(10), transformador puro; moneda CLP y adjudicación protegidas.
- `scripts/cache_y_transformar_compra_agil_mer.py`: conservación privada de respuestas JSON originales fuera del repositorio y reutilización sin reconsulta; `--fetch` habilita solicitud explícita sólo si no hay caché.
- `scripts/resolver_proveedores_ofertas_mer.py`: vincular `id_proveedor` por RUT normalizado con `Proveedores` existente, sin inventar identidad.
- `scripts/planificar_upsert_api_mer.py`: proponer inserciones/actualizaciones por claves y detectar conflictos sin sobrescribir datos.
- `scripts/simular_escritura_api_mer.py` y `scripts/preparar_transaccion_api_mer.py`: simulación offline y respaldo preflight.
- `scripts/exportar_ofertas_resultados_preview.py`: fragmentos públicos aislados y manifiesto; excluye RUT, `id_proveedor` y metadatos de fuente.
- `scripts/validar_preview_api_mer_aislado.py`: contrato preliminar para lector frontend.

En rama `etapa2/escritor-prueba-20261028` / PR #1 (sin fusionar):
- `scripts/escribir_api_mer_libro_prueba.py`: escritor con lock, respaldo local y verificación posterior, bloquea IDs MER del catálogo; solo copia explícita de prueba; no rollback automático.
- `scripts/ensayo_publicacion_api_mer.py`, `scripts/ensayo_integracion_api_mer_actions.py`: flujo sintético integrado de escritura, segunda ejecución idempotente, relectura y exportación preview.
- Workflows `.github/workflows/pruebas-escritor-api-mer.yml`, `.github/workflows/ensayo-api-mer-frontend.yml`, `.github/workflows/integracion-api-mer-ensayo.yml`. El último dispone de `conectado=true` solo bajo configuración explícita; por defecto offline; no consulta ChileCompra y no hace deploy.
- Pruebas en `tests/test_*api_mer*.py` y `tests/test_integracion_api_mer_sin_api.py`. Documentación específica en `docs/INTEGRACION_TRES_TAREAS_GITHUB_ACTIONS_2026-10-28.md`.

## 4. Evidencias de ensayos
- Copia de prueba real del MER: https://docs.google.com/spreadsheets/d/18iPCaHbNTpjIfgMsNu3ZhQ0u9lBqx4_zaDdWgrSkcqY/edit . Se creó por **Google Drive conectado a ChatGPT**; tiene las seis pestañas; se insertó **una oferta sintética** `TEST-API-0001` y **un resultado sintético** del proceso `TEST-20261028-COT26` mediante la conexión de Google Sheets, y ambas filas fueron re-leídas y verificadas. Una lectura posterior confirmó un ejemplar de cada registro, sin reescritura.
- **Distinguir**: escribir desde ChatGPT conectado con Sheets sí funciona; el acceso autónomo desde GitHub Actions necesita **una cuenta de servicio propia o autenticación equivalente**. GitHub Actions no hereda la conexión de ChatGPT. No bloquear la **primera prueba supervisada** por esa configuración.
- Pruebas offline de idempotencia, bloqueo, recuperación ante fallo parcial simulado y exportación: [run 40790921461](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/40790921461) success; [run 40791097164](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/40791097164) success.
- Ensayo integral aislado en Actions: [run 40791690653](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/40791690653) success; [run 40791690798](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/40791690798) success.
- Ningún ensayo ha desplegado datos sintéticos al portal real.

## 5. Limitaciones todavía abiertas — NO declarar producción lista
1. La publicación **operativa** `scripts/exportar_mer_operativo_v2.py`, `scripts/ubuntu_publicar_v2_post_etl.sh` y derivados `.github/workflows/publicacion-v2-post-etl.yml` aún se centra en `Procesos` y `OrdenesCompra`. Aunque `frontend-v2/js/app.js` ya lee `ofertas` y `resultados` cuando hay partes, los datos nuevos de esas tablas **no se exportan/publican automáticamente** con el circuito vigente.
2. El escritor Python del PR #1 fue probado con dobles/in-memory; **no** con cuenta de servicio real de Actions. El acceso de ChatGPT sí hizo inserción/relectura en la copia real.
3. El escritor guarda respaldo pero **no es transaccional entre pestañas** y no dispone de rollback automático; el reintento parcial se comprobó sólo con simulación.
4. No hay aún JSON real conservado de Compra Ágil ni validación documentada de moneda CLP para `monto_total`; tampoco adjudicación V1 confirmada.
5. PR #1 es borrador, no fusionado a `main`; no alterar cron/ETL/meses históricos ni publicar pruebas sintéticas.

## 6. Decisión operativa para siguiente chat
El usuario **aprueba continuar con una primera prueba real supervisada de la API**, sin bloqueo por credenciales de Ubuntu o de Actions. Hacer **una consulta controlada** de `839-4-COT26` cuando se autorice la ejecución; guardar JSON privado, transformar a Ofertas/Resultados; contrastar moneda; usar la conexión ChatGPT→Google Sheets para incorporar primero a **copia de prueba**, con deduplicación y lectura posterior. No escribir en MER operativo ni publicar datos reales en Pages hasta completar controles y revisión.

En paralelo o inmediatamente después, cerrar integración real de exportación/publicación de Ofertas y Resultados usando la infraestructura existente, sin reescribir Fase 1. La automatización autónoma en Actions puede configurarse después de la primera prueba supervisada y requerirá credenciales independientes; no convertirlo en impedimento del piloto.

**Principios del usuario:** avanzar con autonomía, sin rondas interminables de aprobaciones; ejecutar tareas completas cuando sea viable; no reconstruir componentes que funcionan; documentar commits/evidencias reales; distinguir ensayos sintéticos, conectores y producción.

## 7. Prompt de continuidad
> Continuemos la Fase 2 del Observatorio de Inteligencia de Mercado Público desde `docs/ESTADO_FASE2_API_CONTINUIDAD_2026-10-28.md` en el repositorio `juliopez/MercadoPublico-Inteligencia`. Revisa PR #1 y la documentación. La Fase 1 (cron Ubuntu, MER y publicación Procesos/OC) está validada y NO debe alterarse. Ya se probó la API V2 con 15 cotizaciones para `839-4-COT26`, pero su JSON original no se conservó. Existen adaptadores, caché, upsert, pruebas offline y copia Sheets de ensayo `18iPCaHbNTpjIfgMsNu3ZhQ0u9lBqx4_zaDdWgrSkcqY`. Quiero cerrar el piloto de Fase 2: capturar una única respuesta API real y conservarla, transformarla al MER, verificar en copia de prueba mediante la conexión Sheets disponible y completar el encaje con la publicación existente de Ofertas/Resultados. No exijas credenciales Ubuntu o GitHub Actions para la prueba supervisada desde ChatGPT; no publicar datos sintéticos ni tocar históricos, y documenta evidencia y pasos faltantes de manera precisa. Evita consultas reiteradas a la API.
