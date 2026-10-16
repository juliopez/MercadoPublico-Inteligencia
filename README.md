# Observatorio Mercado Público — marcha blanca manual

## Arquitectura
ChileCompra (API V1 y V2) → ETL GitHub Actions → Google Sheets (fuente canónica) → JSON público → GitHub Pages (frontend `index.html`).

**No hay cron activo.** No se consultan las API al abrir el frontend. El repositorio no contiene credenciales. Secretos: `CHILECOMPRA_TICKET`, `GOOGLE_SERVICE_ACCOUNT_JSON`. Variable: `GOOGLE_SHEET_ID`.

## Operación diaria
Abrir [Actions → Marcha blanca - operaciones manuales](../../actions/workflows/marcha-blanca-manual.yml) y seleccionar **Run workflow**.

Opciones:
- `licitaciones`: sincroniza procesos y consulta detalles de adjudicación disponibles en API V1. Las ofertas individuales no se inventan cuando la API no las suministra.
- `compra_agil`: sincroniza procesos y obtiene detalle de cotizaciones/selecciones correspondientes a los procesos del día.
- `ordenes_compra`: sincroniza listado oficial de OC en `OrdenesCompra`.
- `publicar`: exporta exclusivamente información pública de Google Sheets a `data/observatorio.json` y despliega Pages, sin llamar ChileCompra.
- `completa`: ejecuta las tres categorías y después publica si todas finalizaron correctamente.

**Fecha**: `AAAA-MM-DD`, obligatoria en el formulario; no se infiere la fecha actual. Se rechazan fechas inexistentes o futuras. La misma fecha puede ejecutarse nuevamente para recuperar fallas. En la opción `publicar`, la fecha introducida no filtra los datos: se exporta el estado actual completo de Sheets. Máximo 3 intentos por componente en el workflow; entre fallas, se conserva la información anterior. Los registros ausentes en respuestas de la API no se interpretan como eliminaciones.

Para desplegar únicamente cambios del frontend, existe el workflow manual `pages.yml`.

## Esquema y limitaciones
La Google Sheet principal tiene `Procesos` (16 campos), `Ofertas` (7), `Resultados` (10), `OrdenesCompra` (10), además de `Control`, `Indicadores` e histórico de agosto. Los archivos históricos se importan separadamente; el proceso diario no sustituye esa carga.

El ETL de detalle de Compra Ágil cubre cotizaciones disponibles para los procesos seleccionados, no garantiza que todas sean públicas. En licitaciones, el detalle V1 permite adjudicaciones cuando estas se informan pero no garantiza el universo de ofertas individuales. La publicación conserva la última versión si la exportación falla. La extracción completa y la compatibilidad con volúmenes históricos grandes requieren validación operativa antes de declarar producción.

## Recuperación y respaldo
Rama: `respaldo-pre-limpieza-marcha-blanca-20261016`.
Los errores de GitHub Actions quedan visibles en el log de ejecución. Para reintentar, repetir manualmente la categoría y fecha fallidas; luego ejecutar `publicar`.
