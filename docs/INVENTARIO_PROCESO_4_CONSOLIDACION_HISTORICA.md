# PROCESO 4 — Consolidación histórica definitiva, día 10 hábil

> **Estado: código de cadena automática desarrollado en GitHub; servicio/timer actualizado e instalado en Ubuntu según captura del usuario del 31/10/2026, 00:18.** Sigue pendiente la **primera ejecución productiva integral** con ZIP oficiales, escritura y verificación final; no declarar «validado de extremo a extremo» antes de su evidencia. **No se requiere aprobación humana mensual en el diseño.**

## Objetivo, calendario y control
Consolidar de forma autónoma **el mes calendario anterior** usando las **tres fuentes oficiales mensuales** (licitaciones, cotizaciones Compra Ágil y órdenes de compra), incorporar altas y cambios pertinentes a las seis pestañas de Google Sheets MER, verificar integridad, republicar histórico consolidado y **emitir la constancia terminal solo después de comprobar la publicación**.

- Temporizador Ubuntu `deploy/systemd/mercadopublico-conciliacion.timer`: evaluación diaria `OnCalendar=*-*-* 10:00:00`, `OnBootSec=10min`, `Persistent=true`. La puerta de negocio habilita ejecución desde el **día 10 o siguiente hábil de Chile**, y sigue reintentando los días hábiles si continúa pendiente.
- Servicio `deploy/systemd/mercadopublico-conciliacion.service`: `ExecStart=/bin/bash scripts/ubuntu_preparar_conciliacion_persistente.sh`, `TimeoutStartSec=6h`. No hay GitHub Action encargado de iniciar la carga en Sheets; GitHub se usa para guardar datos públicos, derivados y Pages.
- El 31/10/2026 se observó en Ubuntu `enabled`, `active`, el listado de próxima ejecución del timer y `TIMER_CIERRE_AUTOMATICO_INSTALADO`. **No se ejecutó una consolidación real en esa instalación**.

## Flujo extremo a extremo

| Nº | Etapa | Función, criterio de éxito | Ejecutor |
|---|---|---|---|
| 1 | Programación y ventana | Timer, bloqueo `flock` compartido; feriados comprobados; `PENDIENTE_CONCILIACION` | `mercadopublico-conciliacion.timer/.service`, `ubuntu_preparar_conciliacion_persistente.sh`, `verificar_ventana_conciliacion.py` |
| 2 | Descarga oficial mensual | Obtener tres ZIP de mes anterior, CRC, SHA-256, reusar descargas válidas | `orquestar_cierre_mensual.py`, `config/fuentes_descarga_mensual.json` |
| 3 | Normalización | Importar tablas MER, producir CSV, SQLite y conteos; revisar seis cabeceras | `importador_historicos_v2.py` |
| 4 | Diagnóstico y política | Snapshot de Sheets, diferencias de claves/campos, auditoría y precedencia oficial | `diagnosticar_cierre_integrado.py` y ejecutores auxiliares |
| 5 | Escritura histórica | Respaldo previo, aplicar conciliación a las seis tablas, preservar registros solo operativos | `cierre_mensual_automatico.py` → motor de `ejecutar_cierre_supervisado.py` / `cargador_cierre_mer_v2.py` |
| 6 | Verificación de datos | Lectura posterior de seis tablas, conteos y evidencia de respaldo/constancia de carga | `constancia_carga_real.json` y estado local |
| 7 | Republicación V2 del histórico | Exportador separado del diario; cuatro entidades; recalcular búsqueda, perfiles, analítica e índices; commit/push | `exportar_mer_historico_conciliado_v2.py`, `publicar_cierre_historico_v2.py` |
| 8 | Comprobación remota | Confirmar workflow de Pages y consulta HTTP de catálogo/analítica del histórico | `publicar_cierre_historico_v2.py`, GitHub Actions/Pages |
| 9 | Estado terminal | Actualizar catálogo privado y estado local a `CONCILIACION_HISTORICA_VERIFICADA` **solo después** de evidencia anterior | `cierre_mensual_automatico.py`, `config/catalogo_sheets.json`, `estado_cierre.json` |

## Inventario técnico
**Entradas principales:** `scripts/ubuntu_preparar_conciliacion_persistente.sh`, `scripts/cierre_mensual_automatico.py`, `scripts/verificar_ventana_conciliacion.py`, `scripts/orquestar_cierre_mensual.py`, `scripts/diagnosticar_cierre_integrado.py`, `scripts/ejecutar_cierre_supervisado.py`, `scripts/cargador_cierre_mer_v2.py`, `scripts/exportar_mer_historico_conciliado_v2.py`, `scripts/publicar_cierre_historico_v2.py`; auxiliares de diagnóstico y generación de índices siguen siendo dependencias.

**Timer y servicio:** `mercadopublico-conciliacion.timer/.service`. **Instalador verificado por el usuario:** `scripts/instalar_cierre_mensual_automatico_ubuntu.sh`.

**Archivos de estado locales (privados):** `~/.local/share/mercadopublico/cierres/<periodo>/estado_cierre.json`, `preparados/informe.json`, `preparados/preparado.sqlite`, `resumen_diagnostico_cierre.json`, `precedencia_oficial_mensual.json`, `constancia_carga_real.json`, respaldo verificable. **No eliminar por limpieza del repositorio.**

**Datos externos:** Google Drive/Sheets de mes anterior; catálogo privado; `frontend-v2/data/`; GitHub Actions y GitHub Pages. Credenciales sólo locales Ubuntu. **Bloqueo compartido** `logs/.mer_escritura_compartida.lock`.

## Evidencia, riesgos y aceptación
- **Instalación del timer:** confirmada por captura del usuario el 31/10/2026 a las 00:18; `enabled`, `active`, próxima evaluación 10:00.
- **CI estática:** validaciones de sintaxis y conexiones documentadas; no prueban escritura real ni despliegue de cierre histórico.
- **Primer ciclo productivo elegible:** 10/11/2026, con octubre como mes anterior. Depende de disponibilidad e integridad de ZIP oficiales.
- **Pendiente:** confirmar con logs y constancias que Sheets quedó conciliado, GitHub Pages expone los conteos del histórico y el estado terminal quedó registrado. Si falta evidencia o falla una verificación, permanecer **pendiente/bloqueado**, nunca cerrado ficticiamente.
- **Sin intervención humana mensual** para aprobar cargas o marcar cierre; si falla una fuente o infraestructura, reintentos controlados y auditoría de incidentes. No declarar garantías de recuperación de fallos que no se hayan probado.
- **Riesgos abiertos para validación de producción:** comportamiento ante indisponibilidad oficial, corte a mitad de escritura, capacidad temporal de 6h, correspondencia entre commit publicado y comprobación de Pages, y coherencia de las seis tablas.
- **No modificar** las líneas base [Proceso 1](LINEA_BASE_PROTEGIDA_CRON_1600.md) y [Proceso 2](LINEA_BASE_VALIDADA_API_COMPRA_AGIL_400.md).

## Verificación y continuidad
Para inspección **sin escribir**: `systemctl --user status mercadopublico-conciliacion.timer`, `systemctl --user list-timers --all`, `journalctl --user -u mercadopublico-conciliacion.service -n 100 --no-pager`. La salida de instalación no equivale a cierre real.

**Decisión operativa:** proceso 4 desarrollado e instalado, **pendiente de la validación de su primera corrida productiva íntegra**. No confundir con el [Proceso 3 — rotación](INVENTARIO_PROCESO_3_CAMBIO_MES.md).
