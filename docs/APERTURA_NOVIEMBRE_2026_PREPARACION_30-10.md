# Preparación de cambio operativo octubre → noviembre 2026 (30/10)

## Decisión: apertura operativa ≠ cierre histórico
- **Viernes 30/10:** conservar octubre sin trasladar ni clasificar como histórico. No borrar/renombrar Sheets ni reescribir sus filas.
- **Lunes 02/11:** utilizar automáticamente el libro `2026-11` ya registrado como `operativo` en `config/catalogo_sheets.json`. El ETL Ubuntu de las 16:00 calcula el mes vigente con America/Santiago. El nuevo cron API local de las 20:00 debe activarse **solo después de comprobar accesos y ejecución de noviembre**.
- **Martes 10/11:** cierre supervisado de octubre mediante tres ZIP oficiales, conciliación, respaldo, verificación, aprobación y traslado del mismo ID a históricos: `docs/RUNBOOK_CIERRE_2026_10.md`. No anticiparlo a 30/10 ni 02/11.

## Preparación de frontend aplicada en código
En `scripts/exportar_mer_operativo_v2.py`, el exportador ahora registra en el catálogo público el nuevo mes si existe previamente como `operativo` en `config/catalogo_sheets.json`. En el **primer export del mes** genera fragmentos de las cuatro entidades (`Procesos`, `Ofertas`, `Resultados`, `OrdenesCompra`), incluidos fragmentos `[]` para entidades todavía vacías. No modifica octubre ni ejecuta un cierre histórico. La publicación solo se materializa tras la carga ETL validada.

## Verificaciones bloqueantes antes de lunes
1. En Ubuntu, `git pull --ff-only origin main` desde el repo correcto.
2. Confirmar `timedatectl`; Ubuntu debe resolver correctamente noviembre 2026 para el job de las 16:00.
3. Confirmar que el Sheet de noviembre (`1faLUhyB13Qty7dSNqbRHLCmpq-cxgW8bIOgPN0KCWnE`) existe, que tiene **las seis pestañas y las cabeceras SCHEMA**, y que la cuenta de servicio local puede leer y escribir. La entrada del catálogo **no acredita por sí sola** este punto.
4. En Ubuntu: `bash scripts/ubuntu_cron_integrado.sh --verificar`; no consulta API ni escribe en MER.
5. Verificar capacidad de Google Sheets (número de celdas), permisos de Drive y salida del ETL; si falla el preflight, **no activar API local**.
6. Tras ejecución ETL del lunes, comprobar `frontend-v2/data/catalogo-publico.json` con el mes `2026-11` único, cuatro entidades y partes existentes, más índices/analítica de noviembre y Pages.
7. Activar cron API local **solo después** de preparar secrets seguros y comprobar que no se superpone con otro escritor MER. GitHub Actions API automático quedó desactivado.

## Puntos de atención
- En `config/catalogo_sheets.json`, octubre y noviembre todavía figuran como `operativo`; esto responde a una **transición sin cierre físico**. El ETL elige por fecha actual, no por ser el único valor `operativo`. Octubre conserva ese estado **hasta el cierre auditado del 10/11**.
- El mecanismo de cierre no debe depender de que el ZIP oficial mensual esté disponible el primer día hábil.
- La carga API de noviembre debe iniciar una ventana nueva en `control/cola_api_mer.json`, preservando el cursor e historial de octubre.
- Resguardar datos y evitar dos cron simultáneos con escrituras a las mismas tablas; el script local de API deberá utilizar la exclusión compartida con el cron principal o ejecutarse fuera de su ventana.
- **Estado de preparación:** código GitHub preparado, validación de permisos del Sheet noviembre y despliegue real noviembre pendientes.
