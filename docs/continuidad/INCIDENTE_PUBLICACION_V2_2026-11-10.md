# Incidente publicación V2 — 10/11/2026 y corrección propuesta

## Evidencia observada

- 16:02:48 Chile: `salida_operativa/estado_sincronizacion.json` indicó `EXITOSA`, código 0, período 2026-11. La carga MER fue exitosa.
- 16:15–16:48: recuperación API licitaciones: 201 detalles guardados, 196 nuevos en MER, sin errores declarados; no confundir con la variación pública de 78 licitaciones.
- Publicación inicial: `gspread.exceptions.APIError [429]`, cuota `Read requests per minute per user` de Google Sheets. El ETL no debe repetirse por esta falla.
- Recuperación controlada: commit `cad2006aa` enviado a main; workflow Pages #371 falló por timeout; #372 finalizó `success`.
- Frontend observado: período 2026-11, 5.661 registros, 1.263 licitaciones, 4.398 compras ágiles, publicación 16:05 Chile. La diferencia respecto a 5.583/1.185 fue +78.

## Cambio preparado (rama fix/publicacion-v2-reintentos-20261110)

En `scripts/ubuntu_publicar_v2_post_etl.sh`, las **exportaciones de lectura** desde Sheets tienen hasta cuatro intentos, con pausas de 70, 140 y 280 segundos **solo ante 429/cuota**. Cualquier otra falla se propaga de inmediato. No se reejecuta ETL, no se escriben nuevamente las seis hojas MER, no se omiten locks, verificación de carga ni protección frente a cambios locales.

## Alcance y pendientes

- **No confundir código en rama con instalación Ubuntu:** hasta incorporar el cambio en main y ejecutar `git pull --ff-only` en Ubuntu, el cron seguirá utilizando su versión local.
- **No se ha validado en producción un 429 inducido ni un ciclo completo desatendido.** Debe probarse con simulación controlada y revisar logs del siguiente cron.
- El timeout de GitHub Pages es un incidente distinto. El éxito de #372 no demuestra que siempre exista reintento automático. Falta inspeccionar los workflows de despliegue, sus reglas de concurrencia y sus verificaciones de publicación antes de modificar su configuración.
- Una falla persistente de Sheets después de los cuatro intentos aún requiere recuperación posterior; esta rama no instala un nuevo timer ni promete autorrecuperación total.

## Criterio de cierre

1. El ETL deja constancia `EXITOSA` y código 0, independiente del publicador.
2. Si la lectura de Sheets recibe 429, se observa pausa/reintento sin duplicar carga MER.
3. La publicación registra commit, éxito de Actions Pages y comprobación del catálogo publicado, o queda explícitamente pendiente con causa.
4. El proceso se ejecuta sin intervención en al menos un ciclo real, con logs y sin alteraciones indebidas de archivos locales.
