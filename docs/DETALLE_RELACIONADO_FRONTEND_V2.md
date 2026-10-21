# Detalle relacionado por proceso — MER v2 (21-10-2026)

## Objetivo y alcance implementado

Conservar la navegación por bloques validada por el usuario y añadir a **Ver detalle** de la entidad `Procesos` las relaciones públicas por el mismo `codigo` de proceso **dentro del período seleccionado**:

- `Ofertas.codigo` → `Procesos.codigo`.
- `Resultados.codigo` → `Procesos.codigo`.
- `OrdenesCompra.codigo_proceso` → `Procesos.codigo`.

Las relaciones se muestran en paneles separados debajo de la ficha del proceso. Cada panel permite revisar **todos los registros localizados de 10 en 10**, no se descartan resultados después de los 30 primeros. Para otros tipos de entidad se mantiene la ficha básica existente.

La relación por código constituye una **asociación técnica**; no demuestra por sí sola adjudicación contractual. La interfaz expone `validado`, `estado_verificacion_oc` y `seleccionado` tal como fueron publicados; no transforma esas etiquetas en adjudicación.

## Implementación

- Exportación histórica: sin cambios; se reutilizan los fragmentos JSON públicos ya generados en `frontend-v2/data/partes`.
- Generador de índices `scripts/indexar_relaciones_frontend_v2.py`: lee únicamente JSON públicos locales del repositorio y produce `frontend-v2/data/indices/AAAA-MM.json`. No lee ni modifica Google Sheets.
- Índice v2 compacto: una lista de rutas por entidad y un mapa `codigo -> índices numéricos de archivo`. Los índices de junio–septiembre miden aproximadamente 4,6–5,2 MB por mes, en lugar de 22–24 MB que ocupaba el formato redundante inicial.
- Interfaz: `frontend-v2/index.html` + `frontend-v2/js/app.js` + estilos. El índice se solicita **solo al abrir el detalle**, se almacena en caché de sesión y se descargan **únicamente** los archivos referenciados por el código elegido. El listado principal sigue leyendo por bloques y paginando 10 filas.
- Integridad: [workflow de índices](../.github/workflows/indexar-relaciones-v2.yml) verificó los cinco períodos; [ejecución correcta](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39651318772). La vista previa ejecuta `node --check` antes del despliegue.
- Privacidad: no se incorporan RUT ni datos privados en las fichas; se muestran los campos públicos ya exportados. No se escriben hojas ni se altera la versión 1.

## Validación pendiente

La publicación exitosa de GitHub Actions **no equivale** a prueba de clics en navegador. Comprobar para un proceso de junio con ofertas conocidas: `Ver detalle` muestra ficha, cantidad relacionada y paginación; revisar cero, uno y muchos resultados; caso sin relación; acceso a ficha oficial; cambio de mes/entidad durante descarga; integridad de v1. La búsqueda del listado principal sigue acotada al fragmento visible: búsqueda global indexada, perfiles de organismos/proveedores, comparación, favoritos y CSV son etapas posteriores.

**Regla de continuidad:** no sustituir el mecanismo de lectura selectiva del listado por descargas globales. Si el índice no está disponible, mostrar un error en relaciones sin bloquear la ficha básica del proceso.
