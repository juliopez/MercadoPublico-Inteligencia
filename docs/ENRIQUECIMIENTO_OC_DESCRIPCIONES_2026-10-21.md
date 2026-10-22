# Enriquecimiento COT–OC desde descripciones oficiales de OC — junio a septiembre 2026

**Estado:** actualización MER ejecutada y verificada mediante script Ubuntu; registro público publicado en `main`; validación HTTP de GitHub Pages y comprobación visual del navegador aún pendientes. Evidencia de ejecución aportada por el usuario y lecturas directas del repositorio. Fecha de operación: 21–22 de octubre de 2026.

## Contexto y alcance

La auditoría diferencial previa de los ZIP de Compra Ágil encontró **240.649 pares explícitos**, todos en MER, más un vínculo de agosto documentado por separado (240.650 vínculos antes del enriquecimiento). No repetir esa carga. Para encontrar referencias adicionales, se inspeccionaron los ZIP **originales** de Órdenes de Compra de junio–septiembre, identificando `Descripcion/Obervaciones`; el importador MER público no conserva este campo. La identificación desde descripciones es un procedimiento distinto de la conciliación integral por proveedor/unidad aplicada previamente a agosto.

Se produjeron **1.465 vínculos potenciales** con referencias textuales. Validación conservadora: **1.411 aprobables** por evidencia contextual y existencia de proceso COT en MER, **54 separados para revisión**. Las candidatas estadísticas por similitud siguen **no verificadas**.

| Mes | Nuevos vínculos insertados y verificados por Ubuntu | En revisión |
|---|---:|---:|
| Junio | 20 | 3 |
| Julio | 44 | 5 |
| Agosto | 1.222 | 37 |
| Septiembre | 125 | 9 |
| **Total** | **1.411** | **54** |

## Evidencias de operación y protección

- Se crearon copias íntegras de los cuatro libros MER en la carpeta Drive `03_Respaldos`: `RESGUARDO_PRE_ENRIQUECIMIENTO_OC_MER_2026_06_20261021`, y equivalentes 07, 08, 09.
- El primer `--apply` falló HTTP 403; se verificó que la cuenta de servicio tenía permiso **reader** en los cuatro libros. Los permisos se elevaron a **writer** y se verificaron los cuatro mediante Drive.
- La segunda ejecución Ubuntu informó `CANDIDATOS: 1411`, `NUEVOS CON PROCESO COT EXISTENTE: 1411`, `YA EXISTENTES O SIN PROCESO: 0`, y `VERIFICADO` para junio 20, julio 44, agosto 1222 y septiembre 125, con `TOTAL NUEVOS EN MER: 1411`. No repetir `--apply`.
- El script falló **después** de insertar y verificar Sheets, al crear el commit por falta de identidad Git. El usuario configuró identidad local, creó un commit y superó la autenticación `gh` en Ubuntu. El registro actualizado es visible directamente en la rama `main`.
- La lectura directa de `frontend-v2/data/vinculos-oc-verificados.json` confirmó **1.412** entradas: 1.411 incorporaciones nuevas y el vínculo documental previo `839-4-COT26` → `839-10-AG26`. Distribución de ese JSON: junio 20, julio 44, agosto 1.223, septiembre 125.
- El código `frontend-v2/js/app.js` consulta `data/vinculos-oc-verificados.json` en `showVerifiedOC` y excluye esos códigos de la lista de candidatas en la ficha de proceso. **Integración verificada en código**, no equivale a prueba visual.
- La URL publicada en GitHub Pages no fue accesible desde la herramienta de consulta utilizada en esta revisión; **no se certifica** respuesta HTTP 200, despliegue Pages, estado reciente de Actions, ni experiencia en navegador. No modificar frontend ni forzar despliegue sin evidencia de fallo.
- Se conservaron V1, cron diario de las 16:00, ETL, ZIP originales, fragmentos de datos originales y seis tablas MER.

## Precauciones y pendiente

1. **Verificar Pages**, por ejemplo abrir V2 y la ficha de una COT enriquecida y comprobar su OC documentada, o consultar el JSON en el dominio Pages. No confundir publicación en `main` con despliegue ya servido.
2. **54 casos** permanecen sin incorporar y requieren evidencia complementaria; no inferir por semejanza.
3. **Pendiente expresamente diferido por el usuario:** aplicar la metodología integral de agosto (Procesos/Ofertas/Resultados/OC; coincidencias por unidad y proveedor; candidatas aparte) a junio, julio y septiembre. Reutilizar código y resultados, no repetir las cargas COT ni los vínculos ya consolidados.
4. Reconciliar en una posterior actualización `config/catalogo_sheets.json` con las filas nuevas de `VinculosCOT_OC`, tras verificar totales vivos. No asumir que el catálogo se actualizó por el script Ubuntu.
5. Para nuevos meses, el generador de vínculos documentales debe procesar evidencia explícita y publicar el registro actualizado sin modificar manualmente los JSON fuente de OC.

**Estados distintos:** MER actualizado y verificado por script Ubuntu; JSON en GitHub `main` confirmado; integración funcional en código confirmada; despliegue efectivo Pages y revisión visual pendientes.

## Comprobación posterior de integración V2 (21–22 octubre 2026)

Se leyó directamente desde GitHub `main` el registro `frontend-v2/data/vinculos-oc-verificados.json`: 1.412 entradas (junio 20, julio 44, agosto 1.223, septiembre 125). Se contrastó `frontend-v2/js/app.js`: la función `showVerifiedOC` solicita el JSON, selecciona entradas por `codigo_proceso`, y muestra códigos de OC y mes; hay lógica separada que retira las OC verificadas de las candidatas. Caso trazable publicado: `1028871-59-COT26` → `1028871-369-AG26`, de junio.

La consulta externa a `https://juliopez.github.io/MercadoPublico-Inteligencia/frontend-v2/` y a su JSON devolvió acceso no disponible desde la herramienta de navegación; esto **no acredita caída ni publicación exitosa**. La consulta de GitHub Actions asociada al commit documental `1ac8085` devolvió lista vacía; esto **no demuestra el estado de Pages**, que puede usar otra forma de publicación. Siguen **pendientes la comprobación HTTP del recurso servido y una revisión visual real en navegador**. No se dispararon workflows ni se alteraron archivos operativos para una prueba redundante.
