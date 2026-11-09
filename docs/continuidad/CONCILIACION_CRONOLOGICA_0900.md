# Conciliación cronológica matinal del MER — 09:00

**Alta documental:** 2026-11-09, hora de Chile. **Estado:** implementada en `main`, cron instalado en Ubuntu según captura de `crontab -l` aportada por el responsable; **primera ejecución real aún no verificada** (prevista 2026-11-10, 09:00).

## Objetivo y alcance

Revisar el MER **operativo** vigente y trasladar registros que, por su **fecha oficial propia**, correspondan a otro período MER disponible. Es un proceso distinto de la **conciliación oficial de mes vencido P4** (ZIP y cierre histórico), que permanece protegida y sin cambios. Tampoco sustituye el cron 16:00, la API de licitaciones 16:15 ni Compra Ágil 22:05.

## Disparador y archivos

- **Ubuntu crontab:** `0 9 * * 1-5` (lunes a viernes, 09:00, hora local validada frente a `America/Santiago`).
- **Etiqueta:** `# MER_CONCILIACION_0900`.
- **Instalación idempotente:** `scripts/instalar_cron_conciliacion_0900.sh`.
- **Orquestador:** `scripts/ubuntu_conciliar_mer_0900.sh`.
- **Motor:** `scripts/conciliar_mer_cronologico.py`.
- **Log:** `logs/conciliacion_mer_0900.log`.
- **Informe local:** `salida_operativa/conciliacion_cronologica.json`.
- **Publicación:** `scripts/exportar_mer_operativo_v2.py` con autorización explícita `MER_CONCILIACION_PERIODOS=1`; commit/push de catálogo y fragmentos afectados.

## Reglas de clasificación aprobadas

| Hoja MER | Fecha rectora | Conducta |
|---|---|---|
| `Procesos` (licitaciones y Compra Ágil) | `fecha_publicacion` | Clasificar por mes oficial de publicación |
| `OrdenesCompra` | `fecha_creacion` | Clasificar por mes de creación de la OC, aunque el proceso relacionado pertenezca a otro mes |
| `Ofertas` | `fecha_oferta` | Clasificar por fecha propia de oferta |
| `Resultados` | `fecha_resultado` | Clasificar por fecha propia del resultado |
| `Proveedores` | Sin fecha propia | No trasladar automáticamente |
| `VinculosCOT_OC` | Sin fecha propia | No trasladar automáticamente |

Fechas ausentes, inválidas o períodos sin MER histórico configurado: **no se trasladan**; se contabilizan como pendientes. Las relaciones entre entidades se conservan por sus identificadores y pueden cruzar períodos.

## Secuencia implementada

1. Verificar credenciales, entorno, Git limpio y obtener `main` actualizado.
2. Adquirir lock propio `.conciliacion_mer_0900.lock` y lock de escritura compartido `.mer_escritura_compartida.lock`.
3. Leer las cuatro hojas fechadas del MER operativo, determinar destino por fecha propia y elaborar informe.
4. Si hay movimientos, abrir MER históricos configurados y respaldar íntegramente las seis hojas del operativo y de cada destino antes de escribir.
5. Insertar PK faltantes en destino **sin sobrescribir registros históricos existentes**; comprobar PK y contenido de nuevas filas mediante lectura posterior.
6. Retirar del origen únicamente filas verificadas en destino, en orden descendente; comprobar que ya no están en origen.
7. Exportar los períodos afectados y el operativo a fragmentos públicos V2; commit/push para activar la cadena de índices y publicación.

## Limitaciones y riesgos que se deben auditar

- La eliminación en Google Sheets se realiza por filas y puede ser lenta; ante interrupción, el proceso debe reanudarse con las PK restantes, verificando destino. **No asumir atomicidad entre dos hojas.**
- En una PK ya existente en histórico, se conserva el registro histórico, incluso si el operativo posee información más completa; **no existe aún fusión de campos**.
- `Proveedores` y `VinculosCOT_OC` permanecen en el operativo; no hay traslado automático de estas entidades ni exportación pública específica de ellas.
- El proceso puede mover registros a MER históricos, por lo que constituye una **excepción autorizada por el responsable** a la inmutabilidad habitual de históricos. No debe confundirse con una conciliación oficial del día 10 hábil.
- La exportación posterior exige que la conciliación llegue al estado `CONCILIACION_VERIFICADA`; la regeneración final de índices y GitHub Pages requiere auditoría aparte.
- Si se interrumpe después de escribir Sheets pero antes de publicar, debe contrastarse la consistencia entre MER y catálogo.
- Primera ejecución **no validada** al redactar este documento: no afirmar cantidades trasladadas, publicación ni éxito de cron hasta revisar el log y los MER reales.

## Auditoría de primera ejecución — martes 10/11/2026

Consultar en Ubuntu:

```bash
crontab -l | grep MER_CONCILIACION_0900
tail -n 100 logs/conciliacion_mer_0900.log
cat salida_operativa/conciliacion_cronologica.json
```

Contrastar: inicio cercano a 09:00; tabla/mes y PK transferidas; fechas inválidas; respaldo de origen y destinos; relectura y retiro; errores 429/5xx; locks; commit/push; índices derivados y catálogo efectivamente servido por Pages. Si el equipo está apagado o suspendido a las 09:00, el cron local no ejecuta retroactivamente.

## Referencias de implementación

- Motor: commits `ecd0cc9` y corrección de fechas `2a357e1`.
- Exportación histórica habilitada de forma explícita: `5d18a8a`.
- Orquestador: `350bac6`.
- Instalador: `818ff63`.
- Instalación en Ubuntu: captura de `crontab -l | grep MER_CONCILIACION_0900` del 09/11/2026.
