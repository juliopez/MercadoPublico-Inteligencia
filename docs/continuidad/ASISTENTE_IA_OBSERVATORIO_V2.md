# Asistente IA del Observatorio Mercado Público V2 — plan integral aprobado

Fecha de decisión: 13/11/2026. Estado: **plan integral aprobado; prototipo de backend parcialmente implementado y probado; NO habilitado en el frontend público**.

## Objetivo y alcance
Construir un asistente conversacional de inteligencia de mercado basado exclusivamente en los datos públicos del Observatorio V2. Gemini interpreta preguntas y, cuando corresponda, redacta explicaciones; **nunca inventa ni calcula cifras de mercado**. Los resultados numéricos proceden de funciones deterministas, con fuentes, período, cobertura y fecha. Mantener Cloudflare Workers y Gemini en modalidades gratuitas **sin activar facturación**.

## Estado real verificado al aprobar el plan
- Cloudflare Worker externo `observatorio-mercado-publico-ia`: rutas `GET /health` y `POST /chat`, secreto `GEMINI_API_KEY`; modelo probado `gemini-3.5-flash`. El código del Worker reside en Cloudflare, **no se considera versionado ni desplegado automáticamente por este repositorio**.
- Noviembre 2026: respuesta verificada por el usuario: 9.078 procesos, 1.458 licitaciones y 7.620 compras ágiles.
- Agosto 2026: respuesta verificada por el usuario: 83.944 procesos, 8.230 licitaciones y 75.714 compras ágiles; método `conteo_determinista_agregado`.
- La lectura directa de 84 fragmentos de agosto produjo error genérico; se sustituyó por catálogo más agregado `data/analitica/2026-08/procesos.json`, con éxito.
- Se contrastaron en GitHub los seis períodos junio–noviembre 2026: `data/analitica/YYYY-MM/procesos.json` tiene `registros` igual a `catalogo-publico.json.periodos[].conteos.procesos`; la lista `modalidades` permite separar Licitación y Compra Ágil.
- `scripts/asistente_ia/contar_modalidades.mjs` es un módulo exploratorio aislado, no parte del ETL productivo. Su ejecución integral en Node no está acreditada.
- **No existe aún evidencia de pruebas de carga, limitación de abuso, seguridad integral, consultas por empresa, organismos, palabras clave o comparación, ni integración visual.**

## Arquitectura adoptada
```
Frontend V2 (widget aislado, bandera desactivada por defecto)
  -> Cloudflare Worker: validación, cuotas, enrutamiento, errores
  -> intérprete de intención Gemini (estructura cerrada; opcional)
  -> motor determinista de consultas a catálogo, agregados e índices públicos
  -> respuesta estructurada: datos, fuentes, fecha, cobertura, advertencias
  -> Gemini opcional para explicación basada exclusivamente en datos devueltos
```

La disponibilidad de Gemini no debe condicionar las consultas deterministas. No enviar claves, datos privados de MER, hojas privadas, RUT u otros datos personales no necesarios. Los textos recuperados son datos no confiables, no instrucciones. CORS **no** sustituye control de acceso, cuotas ni protección de abuso.

## Funcionalidades comprometidas
1. Conteos por modalidad y período (prototipo probado en agosto y noviembre).
2. Comparaciones temporales y evolución mensual.
3. Búsqueda por palabras clave.
4. Consultas por organismo comprador.
5. Consultas por proveedor y trayectoria histórica.
6. Comparación entre proveedores.
7. Montos informados con semántica explícita y sin equipararlos a pagos.
8. Ofertas, participantes y competencia, según cobertura.
9. Resultados y selecciones informadas, distinguiendo adjudicación verificada.
10. Órdenes de compra y vínculos con procesos.
11. Relaciones entre procesos, ofertas, resultados y OC.
12. Tendencias y oportunidades, con límites de inferencia.
13. Rankings y actores frecuentes.
14. Filtros combinados por región, temática, período, modalidad y actor cuando los datos lo permitan.
15. Consultas transversales multimes.
16. Explicaciones conceptuales con Gemini.
17. Exportación de resultados verificables, respetando límites.
18. Preguntas de seguimiento con contexto de sesión y sin historial persistente por defecto.

**Regla:** ninguna función se declarará implementada solo por estar en este listado; cada una requiere evidencia, límites de cobertura y pruebas.

## Decisiones técnicas
- Priorizar `frontend-v2/data/catalogo-publico.json`, `frontend-v2/data/analitica/YYYY-MM/{entidad}.json` y otros índices/agregados ya publicados; no leer todos los fragmentos por cada consulta.
- Si un agregado no permite contestar exactamente, usar un índice apropiado, diseñar un derivado aislado con validación y autorización previa o indicar que no hay soporte; nunca estimar un resultado como si fuera exacto.
- Consultas Gemini -> JSON de intención validado por esquema con campos permitidos, límites y funciones enumeradas; prohibido ejecutar SQL o código generado por el modelo.
- Caché con invalidación ligada a `fecha_publicacion`/versión del catálogo; evitar resultados obsoletos, especialmente en mes operativo.
- Validar consistencia entre totales de catálogo y agregados, y distinguir registros de procesos únicos.
- Proteger el endpoint con límites de frecuencia y recursos, control de errores, timeouts y monitoreo técnico sin preguntas completas ni información personal.
- Cuota gratuita agotada: error explícito y degradación funcional sin cargos ni cambio automático a proveedor pago.
- Contrato de salida: respuesta, consulta interpretada, período(s), cifras y unidades, fuentes verificables, cobertura, fecha de publicación, advertencias y método.
- Versionar código y pruebas del Worker en repositorio **aislado del ETL**, antes de nuevas ampliaciones.

## Plan de ejecución aprobado
### Fase 1 — Base técnica
Modularizar Worker y motor; control de abuso, validación de esquema, caché, errores, pruebas automáticas y documentación del despliegue. Criterio de salida: pruebas técnicas y de seguridad básicas aprobadas, sin exposición pública.

### Fase 2 — Motor analítico
Inventariar índices/agregados reales y sus contratos; implementar las funciones deterministas priorizadas (períodos, comparaciones, temas, organismos, proveedores, montos, ofertas, resultados, OC, relaciones y filtros). No crear nuevos agregados productivos sin aprobación. Criterio de salida: batería de consultas con resultados contrastados, incluyendo ausencia de datos y cobertura parcial.

### Fase 3 — Inteligencia conversacional
Intención estructurada, desambiguación, seguimiento contextual, redacción fundamentada y defensa frente a instrucciones maliciosas. Criterio de salida: respuestas fieles a los resultados deterministas y comportamiento seguro ante errores/429.

### Fase 4 — Integración visual
Widget accesible, sugerencias, tablas, fuentes, navegación a registros y exportación; bandera desactivada por defecto. Criterio de salida: pruebas de UX, accesibilidad y rendimiento sin degradación del frontend.

### Fase 5 — Auditoría y publicación
Pruebas de carga dentro del free tier, seguridad, privacidad, exactitud, observabilidad, documentación y aprobación explícita de activación. Criterio de salida: decisión documentada de publicación o bloqueo con causas.

## Restricciones operativas permanentes
- No modificar procesos productivos 09:00, 16:00, 16:15 y 22:05, sus workflows, MER/Sheets, exportadores, frontend ni publicación Pages sin aprobación específica.
- No activar facturación ni claves en navegador o GitHub.
- No presentar ausencia de registros como ausencia de actividad real; no equiparar ofertas, selecciones, adjudicaciones, órdenes de compra y pagos.
- Evitar cambios aislados reiterativos del Worker: implementar por fases y validar con pruebas acumulativas.
- Toda entrega debe documentar estado **implementado / probado / pendiente**, commit y evidencia de validación.

## Referencias
- [Modelo de datos](../MODELO_DATOS.md)
- [Frontend V2](../../frontend-v2/README.md)
- [Catálogo público](../../frontend-v2/data/catalogo-publico.json)
- [Agregado agosto](../../frontend-v2/data/analitica/2026-08/procesos.json)
- [Módulo exploratorio](../../scripts/asistente_ia/contar_modalidades.mjs)
- [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [Gemini rate limits](https://ai.google.dev/gemini-api/docs/rate-limits)
