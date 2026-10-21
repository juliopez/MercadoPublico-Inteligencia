# Perfiles contextuales de organismos y proveedores — V2

**Fecha:** 21-10-2026.

## Contexto y decisión
La interacción completa del buscador global fue validada manualmente por el usuario. Se continuó con la recuperación progresiva de perfiles de V1. Antes de intervenir se revisaron README, índice documental, decisiones vigentes, auditoría V1→V2 y código de frontend V1/V2.

## Entrega inicial
- Botón **Perfil organismo** en Procesos y **Perfil proveedor** en Ofertas, Resultados y Órdenes de compra.
- Panel contextual con nombre, cantidad de registros y tabla de hasta 25 filas del mismo actor dentro de **un solo fragmento ya descargado** (hasta 1.000 registros). No se realiza consulta a Google Sheets ni descarga masiva.
- Al cambiar bloque, período o entidad se cierra el perfil para impedir información obsoleta.
- Se conservan la búsqueda global existente, los 10 registros por página, lectura por fragmentos, vistas de detalle y el aislamiento de V1.

**Limitación explícita:** esto es una **vista contextual**, NO el perfil agregado histórico que ofrece V1. No representa participación ni adjudicaciones totales en el mes. Para obtener totales reales se necesitarán índices/agregados públicos nuevos, generados fuera del navegador, sin descargar todas las ofertas.

## Archivos
- `frontend-v2/index.html`
- `frontend-v2/js/app.js`
- `frontend-v2/css/styles.css`
- `.github/workflows/validar-perfiles-v2.yml`

## Pruebas
Workflow: https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39663563527 (verificar resultado antes de afirmar éxito). Comprueba sintaxis JavaScript y existencia de elementos de fichas. Una prueba de interfaz real sobre perfiles y diseño responsive continúa pendiente.

## Próxima mejora
Perfiles agregados por organismo y proveedor por período, precalculados en proceso separado sobre extractos públicos, con indicadores y detalles de respaldo; nunca calculados descargando todo el mes en el cliente.
