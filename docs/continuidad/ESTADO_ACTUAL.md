# Estado actual — punto de recuperación

**Corte documental:** 2026-11-10, Chile. **Fuente:** documentación del repositorio y confirmaciones de operación aportadas durante la sesión. **No constituye una nueva auditoría de Ubuntu ni una certificación de completitud de datos.**

## Estado por componente

| Componente | Estado documentado | Qué falta comprobar |
|---|---|---|
| Cron Ubuntu 16:00, licitaciones y OC | Cadena productiva validada y protegida | Última ejecución local, conteos y publicación de la fecha auditada |
| API Compra Ágil | Lotes de 400; disparador Ubuntu 22:05 hacia GitHub Actions reportado funcionando | Último disparo real, run, checkpoints, 429, persistencia y conteos publicados |
| Rotación mensual | Octubre→noviembre ejecutada y corroborada; timer instalado según runbook | **Siguiente rotación completamente desatendida** y consistencia Drive/Sheets/catálogo |
| Conciliación histórica | Código y timer habilitados según documentación; proceso diseñado sin intervención | **Primera ejecución integral real**: ZIP, seis tablas, respaldo, índices, Pages y constancia |
| Publicación y GitHub Pages | Publicación operativa; frontend consultado satisfactoriamente el 06/11 | Confirmar para cada corrida la correspondencia entre fuente, commit y datos servidos |
| Índices derivados | Generación automática implementada y ejecuciones satisfactorias documentadas | Integridad y sincronización con el catálogo de la corrida examinada |
| Frontend | Seis bloques; consultas y barras de progreso confirmadas funcionales por el responsable | Regresiones futuras y cobertura real, sin inferir completitud |

## Arquitectura vigente

- **Fuentes:** ZIP oficiales ChileCompra y API Compra Ágil.
- **Almacenamiento MER:** Google Sheets/Drive, seis tablas por período.
- **Ejecución:** Ubuntu (cron/timers/disparador) y GitHub Actions.
- **Publicación:** catálogo, fragmentos e índices JSON → GitHub Pages → frontend.
- **Mes operativo documentado:** `2026-11`. Confirmar contra `config/catalogo_sheets.json` y catálogo público en cada nueva sesión.
- **Repositorio público:** https://github.com/juliopez/MercadoPublico-Inteligencia
- **Frontend:** https://juliopez.github.io/MercadoPublico-Inteligencia/

## Prioridades al retomar

1. Revisar evidencia de ejecuciones recientes del cron 16:00 y de la API nocturna, sin alterar sus parámetros.
2. Preparar criterios y evidencia para la **primera conciliación histórica integral**.
3. Verificar la próxima rotación por timer, sin confundir prueba manual con disparo autónomo.
4. Comprobar publicación e índices tras cambios de período y conciliación.

## Restricciones

La [política maestra](../POLITICA_PROTECCION_CUATRO_PROCESOS.md) protege cuatro procesos. **Documentación ≠ prueba de ejecución**; `success` de Actions ≠ cobertura completa; índice faltante ≠ cero actividad. No modificar automatizaciones por trabajo editorial.

## Regla de actualización

Actualizar **fecha de corte**, evidencia, resultados, pendientes y referencias a commits. No sobrescribir un estado no validado con una conclusión optimista. Mantener la última evidencia anterior accesible en el historial Git.

## Contraste adicional — 2026-11-06, 16:22 Chile

Se verificaron en Git los commits `0477f68` (exportación MER noviembre, 19:04:07 UTC) y `bc65f4f` (índices, 19:04:37 UTC). En el catálogo de exportación versionado, las OC de noviembre pasaron de 16.197 a 32.345. Esto acredita **actualización del repositorio**, no certificación del cron Ubuntu ni de Pages. Los runs de Actions, journals Ubuntu y comprobación HTTP permanecen pendientes. El catálogo de configuración mantiene metadatos de inicialización (`filas: 0`), cuya semántica debe verificarse antes de intervenir. Véase [auditoría](AUDITORIA_OPERATIVA.md) y [pendientes](INCIDENCIAS_PENDIENTES.md).


## Actualización del 10/11/2026

- Cron 16:00: carga MER verificada `EXITOSA` 16:02:48 Chile; publicación inicial falló por cuota de lectura Sheets HTTP 429. No confundir con fallo del ETL.
- Cron API licitaciones 16:15: 201 detalles guardados, 196 nuevos en MER; frontend observado con 5.661 registros, 1.263 licitaciones y 4.398 compras ágiles. El incremento visible fue de 78 licitaciones, sin asumir equivalencia con 196 nuevos en MER.
- Publicación recuperada mediante commit `cad2006aa`; Pages #371 falló por timeout y #372 finalizó exitoso.
- Mitigación de 429 fusionada a `main` por PR #10, commit `676e9cf`; instalación Ubuntu y ejecución desatendida aún **no acreditadas**.
- PR #1 y #9: pilotos abiertos, fuera de producción. Ver [iniciativas](INICIATIVAS_EN_DESARROLLO.md) y [incidente](INCIDENTE_PUBLICACION_V2_2026-11-10.md).


## Actualización de evidencia Ubuntu — 10/11/2026, tarde

- `journalctl`: cron 16:00 inició a las 16:00:01; AUX-1615 inició 16:15:01 y cerró sesión 16:48:32 (Chile). El cierre de sesión no certifica por sí mismo éxito de cada etapa.
- `logs/licitaciones_api_1615.log`: 975 códigos únicos listados, 201 detalles guardados, 774 pendientes, 196 registros nuevos en MER, 0 modificados y 0 errores declarados; respaldo verificado y `CARGA_LICITACIONES_API_VERIFICADA`. El informe previo a la carga señalaba `escritura_mer:false` y `publicacion:false`, sin contradecir la carga posterior.
- La publicación automática de AUX-1615 terminó con `BLOQUEADO: cambios locales rastreados`. El `git status` posterior mostró únicamente archivos no rastreados; las comprobaciones de cambios rastreados y preparados dieron 0. **No se ha establecido la causa del estado distinto a las 16:48**; no atribuirlo a un defecto del script.
- A las 18:35:22 Chile el HEAD local fue `676e9cf` (PR #10, mitigación 429). La salida posterior de `git pull` durante la publicación manual avanzó hasta `d5b20cb37`; no confundir la mitigación 429 de P1/PUB-V2 con la causa del bloqueo de AUX-1615.
- Ejecución manual `bash scripts/ubuntu_publicar_v2_post_etl.sh --aplicar`: `EXPORTACION_V2_VERIFICADA`, 5.857 procesos de noviembre, 49.866 OC, 4.915 documentales MER, 2.111 nuevos y 6.326 vínculos publicados; commit `c8303ef3c` enviado a `main`, con `CATALOGO_PUBLICO_ACTUALIZADO`. **Esto acredita publicación en repositorio, no todavía éxito de Actions/Pages ni visibilidad individual de las 196 licitaciones**.
- Pendiente: verificar despliegue Pages y conciliación por identificadores de las 196; observar el siguiente ciclo autónomo 16:15 para comprobar que publica sin intervención. No repetir carga MER ni alterar procesos protegidos.
