# Incidente publicación V2 — 10/11/2026 y mitigación incorporada a main

## Evidencia observada

- 16:02:48 Chile: `salida_operativa/estado_sincronizacion.json` indicó `EXITOSA`, código 0, período 2026-11. La carga MER fue exitosa.
- 16:15–16:48: recuperación API licitaciones: 201 detalles guardados, 196 nuevos en MER, sin errores declarados; no confundir con la variación pública de 78 licitaciones.
- Publicación inicial: `gspread.exceptions.APIError [429]`, cuota `Read requests per minute per user` de Google Sheets. El ETL no debe repetirse por esta falla.
- Recuperación controlada: commit `cad2006aa` enviado a main; workflow Pages #371 falló por timeout; #372 finalizó `success`.
- Frontend observado: período 2026-11, 5.661 registros, 1.263 licitaciones, 4.398 compras ágiles, publicación 16:05 Chile. La diferencia respecto a 5.583/1.185 fue +78.

## Cambio fusionado a main (PR #10; commit 676e9cf)

En `scripts/ubuntu_publicar_v2_post_etl.sh`, las **exportaciones de lectura** desde Sheets tienen hasta cuatro intentos, con pausas de 70, 140 y 280 segundos **solo ante 429/cuota**. Cualquier otra falla se propaga de inmediato. No se reejecuta ETL, no se escriben nuevamente las seis hojas MER, no se omiten locks, verificación de carga ni protección frente a cambios locales.

## Alcance y pendientes

- **No confundir código en rama con instalación Ubuntu:** hasta ejecutar `git pull --ff-only origin main` en Ubuntu, el cron seguirá utilizando su versión local.
- **No se ha validado en producción un 429 inducido ni un ciclo completo desatendido.** Debe probarse con simulación controlada y revisar logs del siguiente cron.
- El timeout de GitHub Pages es un incidente distinto. El éxito de #372 no demuestra que siempre exista reintento automático. Falta inspeccionar los workflows de despliegue, sus reglas de concurrencia y sus verificaciones de publicación antes de modificar su configuración.
- Una falla persistente de Sheets después de los cuatro intentos aún requiere recuperación posterior; este cambio no instala un nuevo timer ni promete autorrecuperación total.

## Criterio de cierre

1. El ETL deja constancia `EXITOSA` y código 0, independiente del publicador.
2. Si la lectura de Sheets recibe 429, se observa pausa/reintento sin duplicar carga MER.
3. La publicación registra commit, éxito de Actions Pages y comprobación del catálogo publicado, o queda explícitamente pendiente con causa.
4. El proceso se ejecuta sin intervención en al menos un ciclo real, con logs y sin alteraciones indebidas de archivos locales.

**Estado documental 10/11:** PR #10 fusionado a `main`; no se ha recibido confirmación de `git pull` local en Ubuntu. No declarar mitigación activa en el cron sin esa evidencia.


## Actualización de evidencia Ubuntu — 10/11/2026, tarde

- `journalctl`: cron 16:00 inició a las 16:00:01; AUX-1615 inició 16:15:01 y cerró sesión 16:48:32 (Chile). El cierre de sesión no certifica por sí mismo éxito de cada etapa.
- `logs/licitaciones_api_1615.log`: 975 códigos únicos listados, 201 detalles guardados, 774 pendientes, 196 registros nuevos en MER, 0 modificados y 0 errores declarados; respaldo verificado y `CARGA_LICITACIONES_API_VERIFICADA`. El informe previo a la carga señalaba `escritura_mer:false` y `publicacion:false`, sin contradecir la carga posterior.
- La publicación automática de AUX-1615 terminó con `BLOQUEADO: cambios locales rastreados`. El `git status` posterior mostró únicamente archivos no rastreados; las comprobaciones de cambios rastreados y preparados dieron 0. **No se ha establecido la causa del estado distinto a las 16:48**; no atribuirlo a un defecto del script.
- A las 18:35:22 Chile el HEAD local fue `676e9cf` (PR #10, mitigación 429). La salida posterior de `git pull` durante la publicación manual avanzó hasta `d5b20cb37`; no confundir la mitigación 429 de P1/PUB-V2 con la causa del bloqueo de AUX-1615.
- Ejecución manual `bash scripts/ubuntu_publicar_v2_post_etl.sh --aplicar`: `EXPORTACION_V2_VERIFICADA`, 5.857 procesos de noviembre, 49.866 OC, 4.915 documentales MER, 2.111 nuevos y 6.326 vínculos publicados; commit `c8303ef3c` enviado a `main`, con `CATALOGO_PUBLICO_ACTUALIZADO`. **Esto acredita publicación en repositorio, no todavía éxito de Actions/Pages ni visibilidad individual de las 196 licitaciones**.
- Pendiente: verificar despliegue Pages y conciliación por identificadores de las 196; observar el siguiente ciclo autónomo 16:15 para comprobar que publica sin intervención. No repetir carga MER ni alterar procesos protegidos.
