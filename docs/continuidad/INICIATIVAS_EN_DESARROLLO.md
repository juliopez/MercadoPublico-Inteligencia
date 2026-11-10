# Iniciativas en desarrollo — registro de PR no productivos

**Actualizado:** 2026-11-10 (Chile). **Propósito:** separar proyectos experimentales de procesos operativos y evitar confundir PR abiertos con despliegues.

| PR | Objetivo | Aislamiento y estado | Condición antes de integrar |
|---|---|---|---|
| [#1 — escritor protegido](https://github.com/juliopez/MercadoPublico-Inteligencia/pull/1) | Probar inserciones y actualizaciones de Ofertas/Resultados | Rama `etapa2/escritor-prueba-20261028`, PR borrador; sin API ni MER operativo | CI, ensayo en copia MER, revisar rollback parcial, aprobación expresa |
| [#9 — Ruta B Tordo](https://github.com/juliopez/MercadoPublico-Inteligencia/pull/9) | Evaluar fuente alternativa para Compra Ágil | Rama `feature/compra-agil-tordo-ruta-b`, PR borrador; staging SQLite/CSV/JSON y workflow manual, sin cron ni escritura MER ni cambios API v2/frontend | Verificar frescura posterior al 06/11, cobertura contra fuente oficial, semántica, aprobación expresa |
| [#10 — mitigación Sheets 429](https://github.com/juliopez/MercadoPublico-Inteligencia/pull/10) | Reintentos de lectura en exportación V2 | **Fusionado a main** 10/11, commit `676e9cf4425cea95462b5d493be579801dadf3ab` | Confirmar actualización local Ubuntu y observar ejecución real; no incluye recuperación de timeout Pages |

## Reglas de interpretación

- **PR abierto ≠ funcionalidad instalada.** Los PR #1 y #9 no forman parte de producción.
- **Fusionado a main ≠ instalado en Ubuntu.** El PR #10 requiere actualizar checkout local para afectar el cron.
- **Prueba exitosa ≠ despliegue Pages verificado.** Exigir evidencia de ejecución y de contenido publicado.
- No cerrar ni fusionar pilotos sin una decisión explícita. La [política de protección](../POLITICA_PROTECCION_CUATRO_PROCESOS.md) prevalece.

## Dónde continuar

- [Estado actual](ESTADO_ACTUAL.md)
- [Inventario de procesos](INVENTARIO_PROCESOS.md)
- [Incidencias pendientes](INCIDENCIAS_PENDIENTES.md)
- [Auditoría operativa](AUDITORIA_OPERATIVA.md)
- [Incidente publicación V2 del 10/11](INCIDENTE_PUBLICACION_V2_2026-11-10.md)
