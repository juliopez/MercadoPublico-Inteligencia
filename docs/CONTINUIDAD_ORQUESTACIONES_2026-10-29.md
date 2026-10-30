# Continuidad operativa — 29 de octubre de 2026

> **Documento histórico.** Para el estado vigente desde el 30/10, usar [Estado y continuidad 30/10](ESTADO_Y_CONTINUIDAD_2026-10-30.md). El schedule nocturno de API que aquí se describe fue **desactivado**, y la ejecución local quedó preparada pero no instalada.

## Estado del Observatorio
- Repositorio: `juliopez/MercadoPublico-Inteligencia`, rama `main`. Frontend V2: https://juliopez.github.io/MercadoPublico-Inteligencia/frontend-v2/.
- MER de octubre: Google Sheets operativo, seis pestañas internas (`Procesos`, `Ofertas`, `Resultados`, `OrdenesCompra`, `Proveedores`, `VinculosCOT_OC`). Cuatro entidades exportadas al frontend.
- **Dos orquestaciones independientes**, que no deben fusionarse ni confundirse:
  1. Cron **Ubuntu local**, lunes a viernes, **16:00 America/Santiago**: ETL de licitaciones y órdenes de compra, actualización de MER, exportación al repositorio; GitHub Actions regenera índices, analítica y despliega V2.
  2. GitHub Actions **API ChileCompra Compra Ágil**, hasta **10 procesos por ejecución**; alimenta `Procesos`, `Ofertas` y `Resultados`; cursor y reintentos persistidos; API 429 requiere detener/reintentar sin consultas masivas.

## Evidencia de funcionamiento cron Ubuntu — 29/10
- Exportación Git registrada 16:05 Santiago (commit `b5531b1fb7`).
- Regeneración de índices y analítica GitHub Actions correcta (run https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/40936860577).
- Supervisor informó erróneamente desactualización por comprobar *fecha de último commit* de analítica sin cambios. Corregido en `.github/workflows/verificar-publicacion-diaria-v2.yml`: valida existencia y coherencia de registros catálogo–analítica, no fuerza commit diario. Validación exitosa: https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/40964460237. Se hizo `git pull origin main` exitosamente en Ubuntu después de la corrección.

## Cambio API: 22:30 -> 20:00 Santiago
- Archivo GitHub Actions: `.github/workflows/observacion-api-2230.yml` (**conserva nombre histórico de archivo**); título del workflow ya indica **20h00**.
- Nuevo cron UTC: `0 0,23 * * *`. 23:00 UTC corresponde a 20:00 de Chile en verano (UTC-3); 00:00 UTC corresponde a 20:00 en invierno (UTC-4). La salvaguarda en `scripts/mer_api_incremental_10.py` exige `now.hour == 20` y lunes–viernes en Santiago, salvo variable excepcional `MER_API_RUN_NOW=1`.
- La doble programación UTC emite también disparos fuera de la ventana local: estos deben terminar con `SKIP`, sin consultar API. La hora real del scheduler puede retrasarse y GitHub no garantiza puntualidad.
- **Antecedente del cambio:** run programado https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/40836657060 se inició a las 04:37 de Chile y terminó `success` pero imprimió `SKIP: fuera de las 22 horas America/Santiago`; NO hubo consulta API real.
- **PENDIENTE CRÍTICO:** confirmar la **primera ejecución automática a las 20:00**, revisando no solo conclusión de Actions, sino logs (ausencia de `SKIP`), cantidad de consultas, nuevos procesos/ofertas/resultados, errores HTTP 429, Google Sheets, exportación y frontend. La primera ejecución a las 20:00 todavía **no ha sido validada** en esta documentación.
- No hace falta ejecutar pull en Ubuntu para activar el cambio del workflow remoto, pero mantener clon local sincronizado para futuras operaciones.

## Integridad y mejoras recientes
- Se corrigieron rutas oficiales de API: `payload.institucion.organismo_comprador`, `payload.estado.glosa`, `payload.presupuesto.monto_disponible_clp`, `payload.resumen.total_ofertas_recibidas`, `proveedores_cotizando[].codigo_empresa`. Reparación: 9 procesos y 71 ofertas enriquecidas; una incidencia previa de Google Sheets en `608-6187-COT26` quedó con reintento.
- El frontend `Resultados` muestra `proveedor_seleccionado` derivado por `codigo + id_cotizacion` desde `Ofertas`, **sin afirmar adjudicación formal**. Montos CLP y adjudicaciones quedan en blanco sin verificación oficial.
- Gráfico de cobertura mensual: barras apiladas al 100% para composición Licitación / Compra Ágil, totales y desglose; octubre parcial.
- No inferir que un workflow con `conclusion: success` necesariamente hizo consultas; revisar siempre resultados y `SKIP`.

## Objetivo prioritario próxima sesión
**Escalamiento de la orquestación API:** medir capacidad real y evaluar **varias ejecuciones durante el día o lotes distribuidos** para superar 10 procesos, considerando que pueden ingresar más de 100 procesos diarios. Medir latencia, errores 429, cuota de Sheets, retraso del scheduler, acumulación de pendientes, idempotencia y consistencia. Mantener Ubuntu 16:00 intacto y reutilizar MER y cadena de publicación. No subir límites a ciegas.

## Inicio recomendado de nuevo chat
> Continúa Observatorio Mercado Público desde `docs/CONTINUIDAD_ORQUESTACIONES_2026-10-29.md` y el README. Antes de modificar nada, revisa en GitHub el primer disparo real de Compra Ágil programado a las 20:00 de Santiago (archivo `.github/workflows/observacion-api-2230.yml`). Diferencia ejecución exitosa de sincronización efectivamente realizada (descarta `SKIP`), registra consultas, nuevas filas y errores. Luego diseña la ampliación gradual a ejecuciones diarias distribuidas, con cuotas, reintentos, cola persistente y sin cambiar cron Ubuntu 16:00 ni el MER existente. Implementa de forma incremental, prueba y documenta resultados.
