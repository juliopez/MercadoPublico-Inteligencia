# Bitácora de continuidad — prueba productiva API Compra Ágil de hasta 400 (30/10/2026)

**Referencia horaria:** America/Santiago. **Inicio informado por el usuario: 22:30 del viernes 30/10/2026.** Esto registra el inicio comunicado, **no acredita por sí mismo que el proceso haya terminado, ni el tiempo `real`**. Registrar hora de término solo con evidencia de terminal.

## Propósito y criterio de éxito
Medir empíricamente el tiempo total de una ejecución de hasta **400 detalles** (consultas, escritura Sheets, exportación y `git push`); registrar cantidad realmente procesada, rendimiento/hora, aparición de HTTP 429, reintentos, enfriamiento, posibles omisiones, y coherencia final Sheets → catálogo/partes → índices analíticos → GitHub Pages. **400 es máximo solicitado, no éxito garantizado**. El cron ordinario a las 16:00 **no debe alterarse**.

## Comando acordado y autorizado (ejecución manual en Ubuntu)
```bash
git pull --ff-only origin main

time env MER_API_CIERRE_EXCEPCIONAL=auto \
  MER_API_MAX_DETAIL=400 \
  MER_API_DELAY_SECONDS=10 \
  bash scripts/cron_api_compra_agil_ubuntu.sh
```
Ejecutar desde la raíz del repositorio; no lanzar otro escritor simultáneo. El prefijo `time` mide todo el wrapper local (hasta push; el tiempo de despliegue asíncrono de Pages se mide **por separado**). `real` es tiempo de pared; `user` y `sys` son CPU, no tiempo total.

## Estado anterior que NO debe confundirse con la prueba de 400
- El 30/10 se ejecutó prueba productiva de **hasta 100**: `consultados=100`, `procesos=99`, `ofertas=764`, `resultados=74`, `errores=0`, `procesos_enriquecidos=1`, `ofertas_enriquecidos=15`. Exportación de cambios efectuada. Octubre quedó con **3.618 Procesos**, **3.509 Licitaciones** y **109 Compras Ágiles**; esos números son **línea de base anterior a los 400**.
- El frontend mostró inicialmente 3.519/3.509/10 pese a que los datos/índices de GitHub estaban ya actualizados: hubo desincronización entre generación de derivados y despliegue Pages, junto a caché analítica.
- Corrección `2b5d9106d17f21deb33ef0f5e7e5f367c41934d9`: invalidar caché de analítica del frontend y forzar despliegue de índices; workflow [41154399329](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/41154399329) terminó `success`. Usuario **confirmó visualmente** que los nuevos valores aparecían.
- Corrección preventiva posterior `2a75738b74f8d624bf5c4c561d4c14d8dfc8f76d`: en `.github/workflows/preview-frontend-v2.yml` se suprimió el disparo inmediato de Pages por `catalogo-publico.json` y `data/partes/**`, conservando el disparo al finalizar exitosamente publicación de derivados; preflight valida total catálogo/partes/analítica y suma por modalidad. Workflow [41155241176](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/41155241176) terminó `success`. **Advertencia:** estas protecciones reducen la carrera, no sustituyen auditoría del contenido servido por Pages tras cada lote.
- Un workflow de derivados de la carga previa falló por colisión de rebase al existir despachos duplicados (push + `workflow_dispatch`). Se eliminó el despacho manual duplicado del wrapper: el push del catálogo desencadena la derivación.
- Rotación octubre → noviembre **confirmada** el 30/10 20:29: octubre archivado operativamente, pendiente conciliación oficial; noviembre ya preparado. La bandera `MER_API_CIERRE_EXCEPCIONAL=auto` solo permite operar el mes calendario bajo la salvaguarda definida. A partir de noviembre no asumir escrituras en octubre.

## Política API que debe comprobarse durante la prueba
- Pausa mínima 10 s entre **solicitudes HTTP**. Ante HTTP 429: dos reintentos adicionales de 10 s. Tras el **tercer 429 consecutivo**, detener consultas, registrar `pausa_hasta` 60 minutos y conservar cursor/cola.
- Guardar resultados aceptados de forma incremental; exportar/publicar incluso si el lote se interrumpe con menos de 400. No interpretar `consultados` como igual a `procesos nuevos`.
- Se mide una **sola ejecución manual**, no se activa nuevo timer ni se cambia la frecuencia del cron.

## Resultado: PENDIENTE DE EVIDENCIA DE EJECUCIÓN
| Evidencia | Resultado |
|---|---|
| Inicio comunicado por usuario | 30/10/2026 22:30 America/Santiago |
| Fin local / `real` / `user` / `sys` | Pendiente |
| `MER_API_RUN_ID`, período efectivo, `consultados` | Pendiente |
| Nuevos `procesos`, `ofertas`, `resultados`; enriquecimientos | Pendiente |
| HTTP 429: cantidad, primera aparición, reintentos, `pausa_hasta` | Pendiente |
| Errores y cola/cursor al finalizar | Pendiente |
| Exportación, commit y push de `main` | Pendiente |
| Workflow de índices y verificación de agregados | Pendiente |
| Workflow Pages y conteo realmente visible | Pendiente |

## Protocolo obligatorio al finalizar
1. **Preservar salida completa del terminal**, en especial `real`, `user`, `sys`; reporte `control/ultimo_reporte_api_mer.json` (sin secretos), `PAUSA_API_HASTA`, fallos y mensajes de exportación/push.
2. Calcular rendimiento en procesos **realmente consultados** por hora con `consultados / (real_en_segundos/3600)`. Distinguir rendimiento de consulta del de incorporación neta. No extrapolar 400 si se corta antes por 429.
3. Verificar que `frontend-v2/data/catalogo-publico.json` y `data/analitica/<periodo>/procesos.json` concuerden; suma de modalidades = total; índices generados y workflow de derivados exitoso.
4. Comprobar despliegue de Pages **posterior a los derivados** y confirmar recarga de la analítica desde la URL pública; comparar las mismas cifras en Sheets, GitHub y V2.
5. Si aparece `PAUSA_API_HASTA`, **no forzar nueva corrida** ni borrar estado; si falla push, índices o Pages, **no volver a descargar**: solucionar exclusivamente la etapa fallida y preservar la cola.
6. Solo después de resultados medidos, determinar cuántos lotes podrían caber entre **22:00 y 07:00**, descontando esperas y bloqueos; no activar el timer API ni cambiar lotes por suposición.

## Continuidad inequívoca
**La siguiente acción NO es volver a programar, rediseñar ni repetir la prueba.** Pedir/evaluar únicamente el resultado de la ejecución iniciada a las 22:30, completar esta bitácora con métricas y links de Actions, verificar publicación efectiva y luego calcular capacidad nocturna. El criterio de fin es concordancia de datos más medición completa. Mantener el ETL de las 16:00 y la rotación mensual intactos.

## Resultado confirmado — viernes 30/10/2026, cierre 23:48 America/Santiago

**Evidencia primaria:** captura de terminal enviada por el usuario. La prueba había comenzado a las 22:30 según mensaje del usuario; la medición precisa del comando `time` fue `real 78m36,303s`, `user 0m30,989s`; la captura no muestra valor `sys` legible, no inventarlo.

**Respuesta efectiva del ejecutor:** `consultados=400`, `procesos=400`, `ofertas=2178`, `resultados=288`, `errores=0`, `pagina=11`, `periodo=2026-10`, `modo=APLICAR`. Hubo HTTP 429 en dos intentos con espera de 10 segundos, sin tercera respuesta 429 consecutiva ni pausa final. `EXPORTACION_V2_VERIFICADA`; `EXPORTACION_API_REALIZADA 2866`; commit local/push `8d621ac4` (según terminal), activación de publicación derivada por push. La ejecución completó **400/400**; no ejecutar nuevamente para comprobar este mismo lote.

**Rendimiento medido:** 78 min 36,303 s = 4716,303 s; 400/4716,303 × 3600 ≈ **305,32 consultas por hora**, o **11,79 s por consulta incluyendo las otras etapas del wrapper**. Incluye extracción, guardado, exportación y push, **no** el despliegue posterior asíncrono de Pages. Una extrapolación lineal de 9 horas daría aproximadamente 2.748 consultas, pero **no constituye capacidad sostenida certificada** ni contempla pausas futuras por 429.

**Comprobación remota:** catálogo GitHub, octubre: `procesos=4018`, `ofertas=3028`, `resultados=371`, `ordenescompra=142181`; agregado analítico: `registros=4018`, `modalidades=[['Licitación',3509],['Compra Ágil',509]]`. Basal anterior: 3618 total, 109 ágiles; delta +400. El workflow de derivados [41161641956](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/41161641956) concluyó `success`; el workflow de Pages [41161685458](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/41161685458) concluyó `success`; el supervisor [41161685418](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/41161685418) también `success`. **Pendiente:** confirmación visual del Observatorio desde navegador de usuario de octubre = 4.018 total / 3.509 licitaciones / 509 Compra Ágil.

**Siguiente decisión:** calcular capacidad de ventana 22:00–07:00 a partir de 305,32/h, considerando límites de la API, persistencia de la cola, posibles 429 y pausas de 60 minutos. No considerar la prueba automáticamente equivalente a capacidad de procesar todas las cotizaciones diarias; no cambiar cron 16:00 ni activar cron API por esta medición única.
