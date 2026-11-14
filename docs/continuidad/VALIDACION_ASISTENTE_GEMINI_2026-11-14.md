# Validación funcional del asistente Gemini — 14/11/2026

## Alcance y evidencia
Validación manual en el frontend V2 del Observatorio de Mercado Público, mediante cinco preguntas y capturas proporcionadas por el usuario el 14/11/2026 (Chile), aproximadamente entre 19:08 y 19:11. Se verificó la respuesta visible en pantalla; **no se contrastaron independientemente los valores con los JSON de origen**. El Observatorio es de uso personal.

Frontend: https://juliopez.github.io/MercadoPublico-Inteligencia/frontend-v2/

Worker: `observatorio-mercado-publico-ia` (Cloudflare). La URL `/health` devolvió `{"estado":"ok","integracion":"gemini-intencion-motor"}` antes de las pruebas. El despliegue del Worker fue confirmado por el usuario.

## Incidencia y resolución observada
- Antes de la corrección, la consulta de ranking de compradores devolvía un mensaje genérico; Cloudflare registró `ASISTENTE_WORKER_FALLO`, etapa `interpretacion`, código 400.
- El diagnóstico añadido por PR #18 permitió identificar `motivo: JSON_INVALIDO` en el evento de las 19:03.
- PR #19 incrementó `maxOutputTokens` de Gemini de 256 a 2048 y distinguió el truncamiento `MAX_TOKENS`. Sus dos validaciones automáticas finalizaron correctamente; el PR se fusionó y el usuario desplegó el Worker unificado.
- En la repetición de la consulta, el frontend mostró el ranking y Cloudflare registró el POST a `/chat` a las 19:07 sin un error asociado visible en la captura. **La evidencia confirma recuperación funcional; no demuestra de forma aislada que el límite de tokens fuera la única causa.**

## Cinco pruebas funcionales

| N.º | Consulta | Resultado mostrado | Evaluación |
| --- | --- | --- | --- |
| 1 | ¿Cuáles son los 5 organismos compradores con más procesos en octubre de 2026? | Universidad de Chile 2.489; MOP Dirección General de Obras Públicas 1.126; Universidad de Atacama 799; Ejército de Chile 787; Universidad de Valparaíso 782 | Respuesta visible, ranking ordenado, período y fuentes |
| 2 | ¿Cómo varió la cantidad de licitaciones entre septiembre y octubre de 2026? | Septiembre 6.974; octubre 6.895; variación −1,13 % | Cálculo consistente: −79 registros; −79/6.974 ≈ −1,13 % |
| 3 | ¿Cuál fue el monto total registrado en las órdenes de compra de octubre de 2026? | 177.972 registros; 177.972 con monto; CLP 2.010.434.416.071; campo `monto_total_oc_clp` | Respuesta visible; advierte que importes informados no equivalen a pagos comprobados |
| 4 | ¿Cuáles son los 5 proveedores con más registros de resultados en octubre de 2026? | SCM Pharma SpA 405; 3CC SpA 401; Comercial GBG SpA 291; Becrux Labs SpA 260; Inversiones Aitrust SpA 228 | Respuesta visible; **registros de resultados no deben interpretarse automáticamente como adjudicaciones confirmadas** |
| 5 | ¿Cómo evolucionó la cantidad de compras ágiles entre agosto y octubre de 2026? | Agosto 75.714; septiembre 72.459; octubre 85.407 | Serie cronológica visible; variación calculada: −4,30 % y +17,87 % entre meses consecutivos |

Las cinco respuestas mostraron fecha de actualización de datos **14-11-2026** y enlaces «Ver fuente». Los números de esta tabla son los **reportados por el asistente**, no una certificación de los agregados de origen.

## Resultado y límites del cierre
**5/5 pruebas funcionales respondidas en el frontend**, después del despliegue del PR #19. Se considera cerrada la verificación funcional de estas cinco operaciones, **no** una auditoría integral de exactitud de datos, exhaustividad de preguntas posibles, disponibilidad futura o rendimiento del servicio.

## Mejoras no bloqueantes detectadas
1. Mostrar variación absoluta y porcentual en comparaciones mensuales; en la prueba 2 se mostró solo −1,13 %.
2. Usar etiquetas de fuente más informativas que el repetido «Ver fuente».
3. Si se requiere certeza numérica, contrastar por separado los cinco resultados con los JSON publicados y documentar metodología, fecha y diferencias.

## Protección operativa
Esta documentación no modifica el frontend, Worker, cron Ubuntu, ETL, MER, Google Sheets, procesos de descarga ni publicación de datos. No introducir cambios productivos adicionales sin autorización expresa.
