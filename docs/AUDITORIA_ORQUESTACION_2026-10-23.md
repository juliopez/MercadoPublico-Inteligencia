# Auditoría de orquestación — viernes 23 de octubre de 2026, 17:44 Chile

## Alcance
Verificar cron Ubuntu 16:00 → ETL/Sheets y conciliación → exportación/catalogación pública → GitHub Actions 17:00 → índices/analítica → GitHub Pages. Auditoría de solo lectura: sin reejecución ETL ni actualización de Sheets.

## Evidencia directa de GitHub
- Listado de runs de repositorio: 1.047 ejecuciones históricas. Entre las últimas 100 consultadas, **ninguna posterior a 2026-10-23 15:00 UTC (12:00 Chile)** y **ninguna con evento `schedule`**.
- Últimos jobs registrados: commits del cierre UX del 22/10, publicados entre 01:31 y 01:33 UTC del 23/10 (22/10, 22:31–22:33 Chile). No hay corrida visible del workflow `Publicacion V2 posterior al ETL Ubuntu` a las 17:00 Chile del día 23.
- Último commit de `main` consultado: `b06215a5` (2026-10-23 01:33:45 UTC); no se observa hoy actualización automática del catálogo operativo en GitHub.
- Catálogo público octubre: 2.094 procesos, 108.269 OC, Ofertas 0, Resultados 0.
- Analítica pública octubre: procesos con monto 794; suma presupuestos CLP 18.441.856.682; registros procesos 2.094. OC: 108.269.
- Workflow `.github/workflows/publicacion-v2-post-etl.yml` contiene `schedule: 0,15,30,45 20,21 * * 1-5` y guardia explícita `America/Santiago` (`now.hour == 17`). Configuración correcta para Santiago a 17h según estación, **pero ejecución no observada**.
- `preview-frontend-v2.yml` se despliega tras `workflow_run` exitoso de derivados y tras cambios relevantes por push. Al no existir ejecución fresca ni commit de datos, **no se certifica Pages actualizado hoy**. Despliegues anteriores de UX no demuestran actualización del ETL diario.

## Dictamen provisional
**Cadena diaria 23/10: NO CERTIFICADA**, por ausencia de ejecución pública reciente de Actions y de publicación operativa visible. No afirmar que Ubuntu falló: su cron y bitácoras son locales y la ejecución podría haber actualizado Sheets, fallado en exportación o ni haber iniciado.

## Evidencia local requerida (solo lectura)
Ejecutar en Ubuntu sin activar ETL:
```bash
cd "$HOME/Julio Lopez/chilecompra/MercadoPublico-Inteligencia" || exit 1
echo "=== CRONTAB ==="; crontab -l | grep ubuntu_cron_integrado
echo "=== ÚLTIMO ORQUESTADOR ==="; ls -lt logs/orquestador_integrado_20261023*.log 2>/dev/null | head
echo "=== EVENTOS ==="; grep -hE 'ORQUESTADOR|EXITOSA|CARGA_VERIFICADA|CONCILIACION_VERIFICADA|PUBLICACION_V2|ERROR|FALLIDA' logs/orquestador_integrado_20261023*.log 2>/dev/null | tail -45
echo "=== ESTADO SINCRONIZACIÓN ==="; python3 -c "import json; x=json.load(open('salida_operativa/estado_sincronizacion.json')); print(x.get('ultima_ejecucion'))"
echo "=== CONCILIACIÓN ==="; python3 -c "import json; x=json.load(open('salida_operativa/estado_conciliacion.json')); print(x.get('ultima_ejecucion'))"
echo "=== GIT ==="; git status --short; git log -1 --date=iso --format='%h %cd %s'
```
Omitir datos privados de respaldos y credenciales. No ejecutar `--aplicar` durante diagnóstico.

## Hipótesis por discriminar
1. Cron no se disparó o aborto por prevalidación/lock.
2. ETL se ejecutó y Sheets actualizó, pero publicación no produjo commit (validación frescura, exportador, Git).
3. GitHub Actions programado no disparó, quedó suspendido o no encontró cambio fresco; falta averiguar estado del disparador.
4. GitHub Pages recibió solo despliegues anteriores.

## Próximos pasos
Recibir logs Ubuntu y determinar **última etapa confirmada**. Corregir solo la etapa fallida, con nueva auditoría de logs y datos; no repetir ETL ni modificar fuentes históricas mientras el estado de Sheets esté indeterminado.
