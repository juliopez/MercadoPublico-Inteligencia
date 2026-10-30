# Prueba API local aislada — 30/10/2026

## Situación exacta
La prueba anterior de 10 detalles **sí fue exitosa en GitHub Actions (28/10)**. Las sucesivas pruebas de 25 **no llegaron a invocar API en Ubuntu**: faltaba `api.env`, luego bloqueo por archivos Git no versionados, finalmente el mes de octubre archivado bloqueó correctamente la escritura de producción. Octubre sigue histórico y noviembre operativo; no revertir esos estados.

## Solución
Se agregó `scripts/probar_capacidad_api_compra_agil.py`, una prueba aislada que SOLO consulta la API por HTTP GET; no importa gspread, no abre Sheets, no escribe cola, reportes, catálogos ni Git. Usa el ticket privado ya configurado en `~/.config/mercadopublico/api.env`, selecciona octubre con `--periodo 2026-10`, recorre listados paginados de 10 y consulta sucesivos detalles con separación mínima de 3 segundos. Detiene la prueba al observar errores HTTP y emite `RESUMEN_PRUEBA_API` con conteo de llamadas, detalles, páginas, duración y errores.

## Pasos concretos ahora, sin esperar noviembre
```bash
cd "$HOME/Julio Lopez/chilecompra/MercadoPublico-Inteligencia"
git pull --ff-only origin main
set -a
source "$HOME/.config/mercadopublico/api.env"
set +a
.venv/bin/python scripts/probar_capacidad_api_compra_agil.py --periodo 2026-10 --limite 25 --pausa 3
```
Si 25 detalles concluyen sin errores, repetir **una sola vez** con `--limite 50`; no habilitar el timer horario todavía. No publicar el ticket ni contenido de `api.env` en capturas. La prueba utiliza la API oficial y consume solicitudes del ticket aunque no escriba registros.

**Criterio de éxito**: `detalles_correctos == limite`, sin errores HTTP, duración medida. `25` o `50` representan detalles efectivamente obtenidos, no nuevas filas en MER. Prueba sin efecto sobre octubre archivado.

## Próxima etapa
Tras evidencias reales de 25 y 50, evaluar frecuencia horaria, presupuesto de solicitudes, backlog, resiliencia ante 429 y comportamiento de producción al comenzar noviembre. No reactivar la programación GitHub ni tocar cron Ubuntu 16:00. Registrar resultados reales en este documento.

## Resultado real Ubuntu — 30/10/2026, 20:56 Chile
**Prueba de 25: EXITOSA (evidencia captura de terminal aportada por usuario).** Comando `.venv/bin/python scripts/probar_capacidad_api_compra_agil.py --periodo 2026-10 --limite 25 --pausa 3`, usando ticket privado local. Resumen observado: `modo=SOLO_LECTURA_SIN_SHEETS_NI_GIT`, `periodo=2026-10`, `limite=25`, `paginas=3`, `codigos_encontrados=25`, `detalles_correctos=25`, `llamadas_http=28`, `errores=[]`, `duracion_segundos=291.47`. No escribió Sheets, cola, Git ni históricos. Se verificó conectividad, paginación y detalles reales desde Ubuntu; **no se verificó todavía carga productiva ni límite sostenido**. Próxima prueba: `--limite 50 --pausa 3`, manteniendo solo lectura, recopilar rendimiento/429 y documentar. No activar aún timer horario.
