# Decisión aprobada — Orquestación diaria API (Fase 2)
**Aprobación del responsable:** 28-10-2026. **Estado:** diseño aprobado, programación nocturna NO activada todavía.

## Responsabilidades
- **16:00 America/Santiago, lunes a viernes:** mantener SIN CAMBIOS el cron Ubuntu validado, encargado de fuentes históricas, Procesos, OrdenesCompra y relaciones que ya calcula.
- **17:00 o primera ventana disponible:** conservar generación y publicación habitual de catálogo, índices, perfiles y analítica, conforme al workflow vigente.
- **22:30 America/Santiago, lunes a viernes:** nueva sincronización **exclusivamente complementaria** de API ChileCompra, para campos de Ofertas y Resultados que no entrega el ETL y que no pueden derivarse internamente. Nunca reimportar históricos ni reemplazar fuentes consolidadas.
- **Tras sincronización API exitosa con cambios:** segunda publicación de solo entidades/derivados afectados. Sin cambios, ninguna nueva publicación.
- Las 22:30 son una elección operativa dentro del horario nocturno recomendado, no hora de actualización oficial garantizada por ChileCompra.

## Condiciones de seguridad
1. Utilizar códigos ya existentes en MER como universo; seleccionar únicamente los que precisen datos oficiales no derivados. Respetar período de pertenencia: el piloto `839-4-COT26` corresponde a **julio**, no octubre.
2. Deduplicar por `(codigo,id_cotizacion)` en Ofertas y `(codigo,id_cotizacion_ganadora)` en Resultados. No sobrescribir valores validados ni inferir CLP, adjudicación o identidad.
3. Conservar JSON bruto privado y hash; no subirlo a repositorio ni Pages.
4. Respetar cuotas y HTTP 429 mediante límites conservadores, backoff y checkpoints de recuperación. Nunca ejecutar consultas masivas sin establecer presupuesto.
5. Coordinar la escritura con el lock compartido del MER y no iniciar en caso de ETL inconsistente. Fallos API no deben invalidar publicación vespertina.
6. Publicar cuando termine la API correctamente, no por una hora fija; reflejar última sincronización API por separado de la fecha ETL.
7. Cierre mensual: conservar pertenencia histórica del proceso y seguir resultados pendientes sin moverlo de mes.

## Dependencias antes de habilitar 22:30
- Completar matriz campo→origen: ETL, cálculo interno o API.
- Ampliar exportación y derivados operativos para Ofertas/Resultados sin modificar ruta de Procesos/OC.
- Validar escritura automática segura, lock, checkpoints y recuperación bajo una identidad autorizada en infraestructura elegida; ChatGPT conectado no transfiere credenciales a Actions.
- Ejecutar ensayo sin consultas API en copia MER y despliegue aislado, luego activar programación bajo límites.
- Elegir un solo responsable de ejecución nocturna (GitHub Actions o cron Ubuntu); **no activar ambos**.

## Evidencia
Primer piloto de 1 proceso, 15 cotizaciones y 1 selección, escrito y re-leído en copia Sheets: `docs/PILOTO_REAL_API_COT_839-4-COT26_2026-10-28.md`.
PR en desarrollo: https://github.com/juliopez/MercadoPublico-Inteligencia/pull/1
