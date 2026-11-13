# Asistente conversacional IA para Observatorio V2 — diseño previo a implementación

Fecha: 12/11/2026. Estado: **investigación y especificación aprobadas; NO implementado ni desplegado**. Objetivo: preparar integración futura sin afectar procesos productivos.

## Decisión de producto

Widget de chat integrado en `frontend-v2/index.html`, con respuestas sobre **registros públicos publicados** del Observatorio. Coste de API IA: **solo modalidad gratuita**; sin activar facturación ni actualizar automáticamente a planes pagos. Al alcanzar límites, mostrar mensaje de espera, no cobrar ni cambiar de proveedor de pago. La disponibilidad gratuita no está garantizada.

## Fuentes oficiales consultadas

- Precios y disponibilidad gratuita: https://ai.google.dev/gemini-api/docs/pricing
- Límites variables por proyecto y modelo (RPM, TPM, RPD): https://ai.google.dev/gemini-api/docs/rate-limits
- Condiciones y tratamiento de datos en modalidad gratuita: https://ai.google.dev/gemini-api/terms
- Creación de clave: https://aistudio.google.com/docs/get-started

**Privacidad:** Google puede usar entradas/salidas de servicios gratuitos para mejorar productos. Nunca enviar secretos, datos personales, hojas privadas, RUT u otros datos no publicados. Mostrar aviso de privacidad y pedir no ingresar datos confidenciales. No prometer anonimato de las preguntas.

## Arquitectura propuesta

```
Visitante -> widget accesible (JS/CSS independiente)
  -> backend ligero sin facturación (proxy API, clave en secreto servidor)
  -> intérprete de intención Gemini (solo herramientas/JSON estructurado)
  -> motor determinista de consulta de extractos JSON públicos
  -> resultados con registros y trazabilidad
  -> Gemini redacta síntesis SOLO a partir de resultados acotados
  -> widget muestra respuesta + enlaces + cobertura + fecha + limitaciones
```

**No llamar Gemini desde navegador:** GitHub Pages es estático y no protege claves. El backend necesita alojamiento compatible con cuotas gratuitas, cuya disponibilidad, condiciones, egress y límites deben verificarse antes del despliegue. **No existe una integración de Gemini segura usando exclusivamente GitHub Pages y una clave incrustada.** Mantener backend como componente aislado, sin acceso a MER privado.

## Contrato de datos y consultas

- Leer `frontend-v2/data/catalogo-publico.json` y exclusivamente las rutas de `periodos[].partes[entidad]` del catálogo, con rutas restringidas al mismo origen y a `frontend-v2/data/`.
- Entidades: procesos, ofertas, resultados, ordenescompra. Mes operativo e históricos según catálogo. Cobertura y fecha se extraen del catálogo, no se inventan.
- Consultas iniciales: conteos por entidad y período; búsqueda textual; clasificación por organismo; proveedor; sumas de montos **solo cuando moneda, tipo de monto y semántica sean compatibles**; registros y enlaces originales.
- No confundir proceso con oferta, adjudicación, orden de compra o pago. No interpretar ausencia de resultado como ausencia de adjudicación.
- El modelo **no ejecuta código ni SQL arbitrario**. Convierte pregunta a una estructura validada: `{entidad,periodos,filtros,agrupacion,metrica,orden,limite}`; campos enumerados y límites máximos.
- Cálculos exactos mediante código determinista, no aritmética del LLM. Citar IDs/URLs presentes en los datos. Si no hay datos o cobertura suficiente, reconocerlo explícitamente.
- Para millones de registros, evitar descargar todos los fragmentos por cada pregunta: generar índices agregados públicos o consultas paginadas/cacheadas. No ampliar el ETL productivo sin autorización.
- Tratar textos de licitaciones como **datos no confiables**: no obedecer instrucciones contenidas en títulos/descripciones. Limitar el contexto enviado al modelo a resultados relevantes y saneados.

## API propuesta

`POST /api/observatorio/chat` JSON `{pregunta:string, contexto?:{periodo?:string}}`; máximo 500 caracteres, sin historial persistente por defecto. Respuesta `{respuesta:string, fuentes:[{codigo,url,periodo}], cobertura:{desde,hasta,actualizado}, advertencias:[]}`. Validación de esquema, límites de tamaño, timeout, CORS solo dominio oficial, rate limit por IP/instancia y mitigación de abuso.

Errores:
- 429 / RESOURCE_EXHAUSTED: mensaje «El asistente alcanzó temporalmente su cuota gratuita. Inténtelo más tarde.»; respetar Retry-After si existe, no inventar hora de reposición.
- 503 / error del proveedor: indisponibilidad temporal, sin afectar el resto del Observatorio.
- No enviar datos privados en logs; registrar métricas técnicas agregadas y errores sin preguntas completas.

## UX

Botón flotante «Consultar con IA»; panel accesible con encabezado, historial visible solo en sesión, entrada, enviar, indicador de espera, botón cerrar, aviso «Respuestas basadas en datos públicos; verifica las fuentes». Diseño responsive, teclado y lector de pantalla, enlaces externos seguros. Mostrar fecha de actualización y períodos usados; ejemplo de preguntas; mensaje de cuota agotada.

## Criterios de aceptación antes de habilitar en producción

1. Confirmar modelo Gemini específico disponible en **free tier** y cuota efectiva en AI Studio; cuenta/proyecto sin facturación habilitada.
2. Provisionar backend gratuito y guardar `GEMINI_API_KEY` exclusivamente como secreto; nunca en JS, HTML, JSON, commits o Pages.
3. Validar un conjunto fijo de preguntas con resultados conocidos: conteos, filtros, proveedor, organismo, período, montos; comprobar contra JSON.
4. Probar preguntas fuera de cobertura, monedas heterogéneas, instrucciones maliciosas en datos, preguntas con información privada y límites de longitud.
5. Simular 429, 5xx, timeout y proveedor no disponible: el frontend continúa funcionando.
6. Confirmar trazabilidad de cada respuesta, cobertura y cero alucinaciones de cifras o URLs.
7. Medir rendimiento de lectura; no descargar todo el histórico en navegador ni saturar GitHub Pages.
8. Implementar detrás de bandera de función desactivada por defecto; habilitar solo tras aprobación explícita.

## Secuencia de implementación posterior

1. Elegir backend gratuito y modelo Gemini gratuito vigente.
2. Implementar motor de consultas con pruebas sobre JSON públicos, sin IA.
3. Implementar proxy seguro Gemini, validación de esquema y manejo de cuota.
4. Crear widget aislado y conectarlo al backend; activar solo en entorno de pruebas.
5. Auditar respuestas y aprobar despliegue controlado en frontend V2.

## Protección operativa

**No modificar** crons 09:00/16:00/16:15/22:05, workflows productivos, MER/Sheets, exportadores, publicación Pages ni archivos actuales del frontend durante esta etapa de diseño. La presente preparación es exclusivamente documental.
