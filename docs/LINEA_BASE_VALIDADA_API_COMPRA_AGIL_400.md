# LÍNEA BASE VALIDADA — API Compra Ágil, ejecución manual de 400

> **VALIDADA EN PRUEBA PRODUCTIVA EL 30/10/2026. PRESERVAR SU COMPORTAMIENTO Y NO ALTERARLA COMO EFECTO COLATERAL DE OTROS FLUJOS.**
>
> Esta declaración protege la ruta **manual** de ingesta incremental, escritura MER, exportación y publicación. **NO significa que el cron nocturno 21:00–07:00 esté implementado, instalado o validado.** Intervenir componentes compartidos requiere autorización, evaluación de impacto y pruebas; ver también [línea base protegida de las 16:00](LINEA_BASE_PROTEGIDA_CRON_1600.md).

## 1. Alcance y evidencia

Ejecución local Ubuntu iniciada según el usuario a las 22:30 y terminada a las 23:48 del 30/10/2026 (America/Santiago). Medición `time real 78m36,303s`; **400 consultas, 400 procesos incorporados, 2.178 ofertas, 288 resultados y 0 errores**. Hubo HTTP 429 transitorios, recuperados mediante reintentos. Exportación, commit y push completos. GitHub confirmó catálogo y agregados coherentes: **octubre 4.018 procesos = 3.509 licitaciones + 509 Compras Ágiles**. Workflows [derivados 41161641956](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/41161641956), [Pages 41161685458](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/41161685458) y [supervisor 41161685418](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/41161685418): `success`. La confirmación visual del resultado de 400 en un navegador quedó pendiente de evidencia. Consultar [bitácora original](BITACORA_PRUEBA_API_400_2026-10-30.md).

Comando validado (desde raíz del repositorio):
```bash
git pull --ff-only origin main
time env MER_API_CIERRE_EXCEPCIONAL=auto \
  MER_API_MAX_DETAIL=400 \
  MER_API_DELAY_SECONDS=10 \
  bash scripts/cron_api_compra_agil_ubuntu.sh
```
**No volver a ejecutar el mismo lote por una duda de publicación**; revisar primero estado de cola y etapas posteriores. `auto` selecciona el mes calendario si está archivado pendiente de conciliación o el operativo vigente; no autoriza escritura retroactiva a octubre fuera de su mes.

## 2. Seis etapas de la cadena validada

| Nº | Etapa | Función | Ejecutor principal |
|---|---|---|---|
| 1 | Preflight y exclusión | Cargar credenciales privadas, revisar Git, dependencias, mes y bloqueos API/MER | `scripts/cron_api_compra_agil_ubuntu.sh` |
| 2 | Consulta incremental | Listados paginados, detalles hasta el límite definido, intervalo HTTP y reintentos por 429 | `scripts/mer_api_incremental_10.py` |
| 3 | Normalización y persistencia | Adaptar datos a esquemas MER, deduplicar, escribir Procesos/Ofertas/Resultados en Sheets | `scripts/adaptar_detalle_compra_agil_mer.py`, `scripts/normalizar_procesos_api_mer.py`, `scripts/mer_api_incremental_10.py` |
| 4 | Estado y recuperación | Cola/cursor por código, reporte por ejecución, persistencia de pausa/reintentos | `control/cola_api_mer.json`, `control/ultimo_reporte_api_mer.json` |
| 5 | Exportación y Git | Exportar público, validar cambios, commit y push sin duplicar disparo manual de derivados | `scripts/exportar_mer_operativo_v2.py`, `scripts/cron_api_compra_agil_ubuntu.sh` |
| 6 | Derivados y Pages | Generar índices, perfiles, analítica, verificar coherencia y desplegar; supervisor | `.github/workflows/publicacion-v2-post-etl.yml`, `.github/workflows/preview-frontend-v2.yml`, `.github/workflows/verificar-publicacion-diaria-v2.yml` |

## 3. Inventario de ejecutores, datos y dependencias

**Scripts locales principales (5):**
1. `scripts/cron_api_compra_agil_ubuntu.sh` — wrapper de producción manual.
2. `scripts/mer_api_incremental_10.py` — motor incremental, HTTP, deduplicación, escritura y cola.
3. `scripts/adaptar_detalle_compra_agil_mer.py` — adaptación del detalle de la API.
4. `scripts/normalizar_procesos_api_mer.py` — normalización/enriquecimiento de procesos.
5. `scripts/exportar_mer_operativo_v2.py` — exportación pública. Además, el motor importa el esquema desde `scripts/importador_historicos_v2.py` (dependencia compartida, también protegida por el flujo de las 16:00).

**Workflows GitHub directamente asociados (3):** `publicacion-v2-post-etl.yml` (derivados, compartido con cron 16:00); `preview-frontend-v2.yml` (Pages, compartido); `verificar-publicacion-diaria-v2.yml` (supervisor, compartido). **No exclusivos de la API**: cualquier cambio en ellos tiene impacto potencial sobre la línea base protegida de las 16:00.

**Estado:** `control/cola_api_mer.json`, `control/ultimo_reporte_api_mer.json`. **Destino:** MER Sheets del período autorizado; `frontend-v2/data/` en GitHub; V2 en GitHub Pages. **Secretos solo en Ubuntu:** `CHILECOMPRA_TICKET`, `GOOGLE_APPLICATION_CREDENTIALS` o `GOOGLE_SERVICE_ACCOUNT_JSON`. **Exclusión:** locks API y `logs/.mer_escritura_compartida.lock`.

## 4. Garantías observadas y límites no probados

- **Validado una vez:** 400/400, 10 s mínimos entre HTTP, reintentos de 429 que no llegaron al tercer rechazo consecutivo, persistencia MER, exportación, git push, derivados y Pages exitosos.
- **Implementado, pero no comprobado íntegramente en esta prueba:** detención después del tercer 429 consecutivo, pausa efectiva de 60 minutos, reanudación post-pausa, recuperación tras corte eléctrico/internet o fallo parcial de Sheets/Git.
- **No validado:** 400 consultas cada hora ni sostenibilidad de nueve/diez horas continuas, eliminación de todo rezago diario, calidad de datos no observables, timer nocturno.
- El `time real` **no incluye** la terminación asíncrona de GitHub Pages; rendimiento medido ≈ **305,32 consultas/h** de wrapper, no SLA.
- La unidad systemd existente todavía está configurada con **200 detalles por ejecución y `TimeoutStartSec=55min`**, incompatible con el tiempo observado de 400. **No activarla tal como está para 400**.

## 5. Regla de protección y continuidad

- **No modificar la cadena manual validada** ni el cron de las 16:00 durante el desarrollo del futuro controlador nocturno.
- Desarrollar programación, ventana de horario, corte seguro, recuperación y observabilidad como **capas nuevas y separadas**; no reformar código validado salvo necesidad demostrada y autorización explícita.
- Proteger el orden: preflight → API → MER + estado → exportación → push → derivados → Pages. Si falla una etapa tardía, reparar esa etapa sin recapturar registros ya confirmados.
- Registrar respaldo, pruebas de regresión y rollback ante cualquier excepción. Conservar secretos, logs, índices y estados.
- Documento para siguiente etapa: [plan nocturno 21:00–07:00](PLAN_OPERACION_NOCTURNA_API_COMPRA_AGIL_2026-10-30.md). **La ejecución manual validada y la automatización nocturna futura son dos estados distintos.**
