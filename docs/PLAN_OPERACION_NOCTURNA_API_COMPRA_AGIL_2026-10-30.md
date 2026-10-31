# Diseño propuesto — operación nocturna API Compra Ágil (30/10/2026)

**Estado: propuesta documentada, NO implementada ni activada.** Zona horaria operativa: `America/Santiago`. Documento de continuidad del Observatorio Mercado Público.

## Objetivo
Automatizar desde Ubuntu la captura incremental de Compra Ágil publicada diariamente por ChileCompra, mientras el computador permanezca encendido durante la noche, sin afectar el ETL vigente de **16:00** (licitaciones y órdenes de compra), la rotación de meses ni el cierre/conciliación diferida.

**Ventana propuesta:** **21:00–07:00** Chile, todos los días si la cobertura lo exige. La alternativa 22:00–07:00 reduce la capacidad estimada. Esta franja es una **decisión de diseño**, no un cron instalado. No se garantiza recuperar cada proceso publicado en la misma fecha.

## Evidencia empírica (no extrapolar como SLA)
Prueba productiva manual 30/10/2026, inicio informado 22:30, final 23:48: `time real 78m36,303s`, `consultados=400`, **400 procesos nuevos, 2.178 ofertas y 288 resultados**, `errores=0`. Respuestas HTTP 429 transitorias recuperadas mediante reintentos. Rendimiento total del wrapper, incluidos Sheets/exportación/push: **305,32 procesos consultados/hora**. GitHub confirmó catálogo y analítica octubre con **4.018 procesos, 3.509 licitaciones y 509 Compra Ágil**; workflows de derivados, Pages y supervisor terminaron `success`. Pendiente verificar visualmente el sitio después de este lote. [Evidencia completa](BITACORA_PRUEBA_API_400_2026-10-30.md).

Proyección **lineal**, no capacidad validada sostenida:
- 21:00–07:00, 10 h: aproximadamente **3.053** consultas.
- 22:00–07:00, 9 h: aproximadamente **2.748** consultas.
- Estimación histórica de referencia (junio–septiembre): cerca de **3.332 Compra Ágil/día hábil**, derivada de un promedio con **22 días hábiles por mes**; no confundir con demanda diaria real, ni necesariamente con consultas API únicas.
- A ese rendimiento, 3.332 consultas requerirían cerca de **10 h 55 min**, antes de interrupciones adicionales. Por tanto, la ventana de 10 h **podría dejar rezago**. Medir volumen de altas reales, pendientes y duplicados por día; no prometer cobertura total sin evidencia.

## Restricciones del sistema existente, confirmadas en GitHub
- `deploy/systemd/mercadopublico-api.timer`: `OnCalendar=*-*-* *:10:00`, cada hora durante las 24 h. **No equivale a la ventana propuesta**.
- `deploy/systemd/mercadopublico-api.service`: `MER_API_MAX_DETAIL=200`, `MER_API_DELAY_SECONDS=10`, `TimeoutStartSec=55min`. Una ejecución de 400 ya tardó 78 min 36 s, por lo que **el servicio actual no es apto para lotes de 400** sin rediseño. No activar tal cual.
- `scripts/cron_api_compra_agil_ubuntu.sh` usa bloqueo API y bloqueo compartido MER, actualiza cola/reporte, exporta, hace commit/push y activa la generación derivada mediante push. La publicación Pages se valida después, no debe suponerse instantánea.
- Control de 429 existente: 10 s entre HTTP, dos reintentos y, tras el tercer 429 consecutivo, `pausa_hasta` persistente por 60 minutos. Respetar este mecanismo y reanudar desde estado confirmado.

## Diseño antes de activar (pendiente de implementación y pruebas)
1. **Orquestador nocturno único**, con inicio 21:00 y corte de nuevas consultas a más tardar a las 07:00 hora Santiago. Debe reservar margen para escritura final, exportación y push (no interrumpir a mitad una operación ya iniciada). Evitar solapamientos y dobles ejecuciones.
2. **Lotes encadenados y dimensionables según tiempo restante**: hasta 400 solo donde existan mediciones suficientes; el tamaño por defecto de 200 es configuración actual, no un límite de la API medido. No aplicar `TimeoutStartSec=55min` a una tarea >78 min; definir un timeout coherente con la política de interrupción segura.
3. **Idempotencia y recuperación**: conservar códigos completados, cursor, informes, pendientes, reintentos y `pausa_hasta` a través de reinicios, pérdida de red, límites API, fallas Sheets o Git; no duplicar ni saltar procesos. No borrar archivos de estado ni reintentar escrituras dudosas a ciegas.
4. **Gobierno de cuotas**: tratar HTTP 429 como límite real del proveedor; respetar enfriamiento y reducir carga si la frecuencia aumenta. Medir duración separada de consultas, escritura Sheets, exportación, push, generación de derivados y Pages.
5. **Publicación íntegra después de cada lote**: Sheets → exportación → commit/push → generación de índices/agregados → Pages. No desplegar conteos inconsistentes ni lanzar workflows duplicados. Ante fallo de Pages, reintentar solo publicación, no volver a consultar registros ya guardados.
6. **Cierre de jornada e informe**: consignar fecha Santiago, hora inicio/fin, consultas, nuevas filas por entidad, enriquecimientos, errores/429, duración, pendientes antes/después, último cursor, atrasos por fecha de publicación, commits, resultados de Actions/Pages y capacidad real. Distinguir registros recuperados de actividad total del mercado.
7. **Supervisión Ubuntu**: energía/suspensión, red, reinicio, `systemd --user` y linger, zona horaria, logs y espacio en disco. Un computador apagado o suspendido **no puede ejecutar**. No asumir recuperación automática sin prueba real.
8. **Coexistencia segura**: no modificar el ETL de las 16:00; compartir candado de escritura MER, coordinar con rotación del último día hábil y conciliación. En cambio de mes, apuntar solo a operativo vigente salvo excepción validada y acotada.
9. **Pruebas previas a habilitar**: dry run de calendario, ejecución corta real, lotes consecutivos, corte horario, recuperación tras 429 y reinicio, ausencia de concurrencia, escritura/integridad, publicación parcial, cruce de fin de mes y verificación de Pages. Plan de reversión: deshabilitar nuevo timer sin tocar cron 16:00.
10. **Fase inicial supervisada** y medición de varias noches antes de decidir tamaño, frecuencia, extensión horaria o necesidad de infraestructura siempre encendida. No activar por una sola prueba de 400.

## Estado de aceptación y próximos pasos
- [x] Evidencia real de lote manual de hasta 400, tiempo y conteos.
- [x] Publicación derivada, Pages y supervisor de ese lote: workflows `success`.
- [ ] Confirmación visual de 509 Compra Ágil en V2 para octubre.
- [ ] Diseñar/implementar y revisar orquestador y timer de 21:00–07:00.
- [ ] Pruebas técnicas locales, recuperabilidad y cierre por horario.
- [ ] Habilitación **expresa y supervisada** del nuevo timer; **hoy no se habilitó**.
- [ ] Auditoría de días sucesivos para verificar si se reduce el rezago.

**Continuidad obligatoria:** al retomar, comenzar aquí y en [bitácora de prueba 400](BITACORA_PRUEBA_API_400_2026-10-30.md). No repetir la extracción de 400 ni confundir el timer horario actual (200/55min) con el nocturno propuesto. Mantener sin cambios los procesos productivos existentes.
