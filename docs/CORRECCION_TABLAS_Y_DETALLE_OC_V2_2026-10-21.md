# Corrección de tablas y acceso al proceso asociado desde OC — V2

Fecha: 21-10-2026.

## Solicitud
A partir de tres capturas, el usuario observó: (1) columnas estrechas que fragmentan palabras, estados y controles en **Procesos**; (2) campos de validación técnica en **Resultados** que no aportan al usuario; (3) necesidad de navegar desde el `codigo_proceso` de una **Orden de Compra** hacia la información del proceso correspondiente.

## Intervención
Antes de editar se consultaron README, índice documental, decisiones vigentes y código real de `frontend-v2/index.html`, `frontend-v2/js/app.js` y `frontend-v2/css/styles.css`.

- **Tabla Procesos:** clase `process-table` aplicada por entidad, anchura mínima de tabla de 1560 px con desplazamiento horizontal acotado al contenedor, anchos mínimos de Nombre/Organismo/Estado/Acciones, control de saltos de línea y botones de ancho legible. No se altera contenido ni paginación.
- **Resultados:** eliminados de las columnas de consulta `validado` y `estado_verificacion_oc`; también se omiten del detalle visible de la entidad Resultados. Los campos y sus valores siguen intactos en los JSON de origen, como evidencia interna.
- **Detalle OC:** para un `codigo_proceso` sintácticamente válido, se añaden un botón **Ver proceso [código] en el Observatorio** (cambia a Procesos, rellena búsqueda global y la ejecuta en el período seleccionado) y el enlace **Abrir ficha oficial** a Mercado Público en pestaña nueva. La búsqueda puede no encontrar un proceso si ese código no figura entre los registros de Procesos publicados en el período (ej. proceso publicado en otro mes). La apertura desde OC conserva la carga selectiva y no descarga el mes completo.
- **Formato de detalle:** los montos CLP ya se presentan formateados y los campos vacíos indican «No informado».

## Cambios
`frontend-v2/js/app.js`, `frontend-v2/css/styles.css`, `.github/workflows/validar-presentacion-detalle-v2.yml`.

## Estado y evidencia
Workflow [#39671670898](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39671670898), validar conclusión antes de reportar aprobación. Prueba automatizada de sintaxis y presencia de controles; **no sustituye revisión visual de usuario**.

V1, Google Sheets, ETL, fragmentos históricos e índices públicos permanecen sin cambios.
