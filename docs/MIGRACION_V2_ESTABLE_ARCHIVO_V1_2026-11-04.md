# Consolidación del Observatorio V2 como plataforma oficial — 04/11/2026

## Decisión y justificación

Por aprobación expresa del responsable del proyecto, **V2 es la única versión pública estable**, y V1 fue una prueba de concepto de corta duración, abandonada tras su desarrollo. No corresponde mantener dos plataformas activas ni publicar dos copias de la base de datos.

**URL oficial:** <https://juliopez.github.io/MercadoPublico-Inteligencia/>

**Compatibilidad:** el acceso anterior <https://juliopez.github.io/MercadoPublico-Inteligencia/frontend-v2/> muestra una página liviana de redirección que conserva consulta y fragmento de URL. Los recursos `frontend-v2/js/`, `css/`, `data/` siguen bajo el prefijo anterior porque el frontend los utiliza y algunas automatizaciones verifican expresamente el catálogo en `/frontend-v2/data/catalogo-publico.json`.

**Archivo V1:** `historico/v1/index.html`, `observatorio.json` y `README.md`. Esta copia de código e índice es un registro histórico, no una aplicación ejecutable sin sus antiguos datos. Git conserva los fragmentos originales en el historial anterior al retiro.

## Limpieza segura

- Eliminados de `main`: **51 fragmentos JSON exclusivos de la V1** (`data/partes/`, 137.528.681 bytes), el manifiesto de su ubicación original `data/observatorio.json`, el CSV de demostración y el archivo antiguo de cobertura. Permanecen rastreables en el historial Git; no se reescribe la historia ni se promete reducción del almacenamiento acumulado del servidor Git.
- Eliminado `.github/workflows/front-pages.yml`, workflow histórico que podía publicar desde la raíz original y sobrescribir la V2.
- La carpeta activa `frontend-v2/data/` mantiene todos los datos, incluidos archivos grandes y 41.107 fragmentos/índices por un total aproximado de **1.342.336.639 bytes**. Estos **no son basura**: alimentan las búsquedas, análisis, perfiles, relaciones y consultas. No se borró ningún período V2.
- El artefacto GitHub Pages contiene **una única copia** de `frontend-v2/`, el índice oficial en raíz, una redirección desde la URL antigua y una explicación liviana en `historico/v1/`. El histórico pesado de V1 no se publica.

## Proceso automático y límites

1. Los generadores ETL y sus salidas escriben en `frontend-v2/data/` como antes.
2. `preview-frontend-v2.yml` valida catálogo, fragmentos, analítica y sintaxis.
3. `scripts/generar_portada_v2.py` construye en **cada despliegue** `_pages/index.html` a partir de `frontend-v2/index.html`, con base relativa hacia `./frontend-v2/` para no duplicar datos ni tocar el JavaScript de consulta.
4. Se copian los datos de V2 una vez a `_pages/frontend-v2/` y se reemplaza solo su `index.html` por el redireccionador; el resto de rutas de archivos continúa vigente.
5. `actions/deploy-pages@v4` publica la raíz. Una comprobación HTTP posterior verifica la portada estable, la redirección y que el catálogo del sitio coincida con el catálogo de GitHub.

No se modificaron **cron Ubuntu de las 16:00, Google Sheets, API nocturna, rotación mensual ni conciliación del día hábil**.

## Evidencia y reversión

- Archivo V1 previo: commit `6d3a976820bf0613a931c2359fdbe5cf8c0dbe34`.
- Eliminación segura de fragmentos V1: commit `ef80b07919c47ad9e711818105150fd51cf14a5f`.
- Primer despliegue comprobado de portada V2 en la raíz y URL antigua redirigida: [GitHub Actions #41902199948](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/41902199948), **success** (sin prueba HTTP independiente).
- **Verificación HTTP pública posterior confirmada:** [GitHub Actions #41902842469](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/41902842469), **success**, log `PAGES_V2_RAIZ_Y_CATALOGO_VERIFICADOS`: se comprobó mediante HTTP público que la raíz presenta V2 estable, la antigua URL redirige y el catálogo publicado coincide con el de GitHub.

**Reversión técnica:** restaurar desde Git la implementación anterior de `.github/workflows/preview-frontend-v2.yml` para reconstruir la publicación antigua, o deshacer los commits de promoción; para restaurar datos V1 tomar los archivos de la revisión previa. Una reversión de presentación no debe restaurar automáticamente el workflow antiguo de V1 con despliegues redundantes. La reversión se puede hacer sin tocar Sheets, Ubuntu o la API.

**Advertencia:** mantener una única copia no reduce el tamaño de los datos V2; cualquier futura reducción debe comprobar por referencia a índices, catálogos y funcionalidad, con pruebas de regresión antes de borrar.
