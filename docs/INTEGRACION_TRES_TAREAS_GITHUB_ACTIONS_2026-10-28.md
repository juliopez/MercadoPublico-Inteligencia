# Etapa 2 — Integración de tres tareas en GitHub Actions (28/10/2026)

## Entregado
1. **Acceso protegido a Sheets**: workflow `.github/workflows/integracion-api-mer-ensayo.yml`, modo offline predeterminado y modo conectado optativo con secreto `GOOGLE_SERVICE_ACCOUNT_JSON` y variable `MER_API_TEST_SHEET_ID`. El archivo JSON se escribe solo en `RUNNER_TEMP`, no en el repositorio. El código rechaza todos los IDs que figuren en `config/catalogo_sheets.json`.
2. **Conexión de transformación con escritura y exportación**: `scripts/ensayo_integracion_api_mer_actions.py` construye registros sintéticos, aplica el escritor con respaldo/lock, repite la ejecución para comprobar idempotencia, vuelve a leer Ofertas/Resultados y genera JSON públicos compatibles en un directorio temporal fuera del repositorio.
3. **Prueba integral**: CI offline ejecuta el mismo circuito, además de las pruebas de fallo parcial y preview. No invoca ChileCompra ni Pages ni escribe en producción.

## Evidencia de CI
- Workflow integrado: https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/40791690653
- Pruebas offline: https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/40791690798

## Pendientes que no deben declararse completados
- La API de GitHub de este entorno no permite consultar/configurar secretos de Actions; **no se ha demostrado que exista** `GOOGLE_SERVICE_ACCOUNT_JSON` ni `MER_API_TEST_SHEET_ID`. El modo conectado no está probado con identidad de servicio. La copia de ensayo es `18iPCaHbNTpjIfgMsNu3ZhQ0u9lBqx4_zaDdWgrSkcqY`.
- No se habilitó exportación de Ofertas/Resultados en el **publicador operativo** ni se desplegó Pages. El ensayo demuestra formato y coherencia sin riesgo; la activación de publicación efectiva exige cambio controlado del exportador y publicador ya validados.
- La reanudación tras fallo parcial está ensayada con dobles de Sheets, no contra una falla real en Google. No hay rollback automático.
- El PR #1 está en borrador; nada fusionado a main.

## Próximos pasos de habilitación
Configurar secreto y variable del workflow, compartir la copia de prueba con el correo de la cuenta de servicio, despachar `conectado=true`, verificar relectura. Después integrar exportador operativo para Ofertas/Resultados y ejecutar despliegue controlado. Solamente entonces consultar una vez el detalle real de ChileCompra y conservarlo privadamente.

## Seguridad
Prohibido subir JSON crudo con RUT/PII a GitHub o Pages. No volver a descargar históricos ni tocar la cadena del cron para estas pruebas.
