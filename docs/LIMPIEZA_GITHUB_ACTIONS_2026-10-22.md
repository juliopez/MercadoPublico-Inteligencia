# Limpieza conservadora de GitHub Actions — 22/10/2026

## Motivación
Eliminar workflows experimentales, duplicados y programaciones heredadas que compiten con el ciclo actual Ubuntu 16:00 / GitHub Actions 17:00. No modificar scripts, Google Sheets, datos públicos, ni cron Ubuntu.

## Resultado comprobado
Se enumeraron directamente los archivos bajo `.github/workflows`. Inventario antes: **35**; después: **28**. Se retiraron de `main` los siguientes siete workflows (recuperables vía historial Git):

| Workflow retirado | Motivo |
| --- | --- |
| `observatorio-unico.yml` | Orquestador V1 con cuatro disparos UTC diarios; conflicto funcional con el ciclo Ubuntu actual |
| `publicar-sheets-pages.yml` | Publicación V1 legacy desde Sheets, redundante con arquitectura nueva |
| `publicar-solo-sheets.yml` | Segundo publicador V1 de Sheets/Pages, redundante |
| `auditar-vinculo-ca-oc-v2.yml` | Auditoría puntual del caso COT–OC ya documentada |
| `conciliar-agosto-ca-oc-v2.yml` | Experimento de agosto cerrado; motor y evidencias permanecen |
| `consolidar-vinculos-mer-agosto-v2.yml` | Consolidación puntual agosto ya ejecutada |
| `verificar-oficial-ca-oc-v2.yml` | Verificación única documentada, no mantenimiento ordinario |

## Workflows protegidos
- `publicacion-v2-post-etl.yml`: regeneración diaria 17:00 hora Santiago, vigente.
- `preview-frontend-v2.yml` y `front-pages.yml`: despliegue Pages V2 y V1 ante cambios.
- `validacion-mer.yml`: validación transversal al actualizar código.
- `publicar-frontend-v2.yml`: exportación manual por período de respaldo; NO confundir con cron.
- Generadores manuales/históricos de índices, analítica, perfiles, autocompletar, búsqueda y sugerencias: aún útiles para regeneración o recuperación, no eliminados.
- Validadores específicos de UI: conservar hasta contar con una prueba de regresión consolidada equivalente; su existencia no implica ejecución diaria.

## Seguridad y verificación pendiente
- La eliminación de un archivo workflow de `main` no borra el historial de ejecuciones ni los commits previos.
- Verificar GitHub Actions y Pages tras el cambio. El hecho de que los archivos existan o se hayan eliminado no constituye un despliegue verificado.
- Si un workflow retirado fuera necesario para recuperar una publicación V1, restaurar el archivo desde Git; no regenerar datos privados o históricos automáticamente.
- El cron Ubuntu 16:00 es independiente y no fue modificado por esta limpieza.
- La integración API de Compra Ágil permanece diferida.

**Próxima revisión:** inspeccionar usos y disparadores de los 28 restantes después de verificar el ciclo automático, antes de retirar validadores especializados.
