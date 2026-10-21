# Comparación de proveedores — Frontend V2

Fecha: 21-10-2026.

## Antecedentes
El usuario confirmó la validación visual de perfiles agregados y aprobó continuar. Se consultaron README, índice documental, decisiones técnicas, el documento de perfiles y los archivos vigentes.

## Funcionalidad
Se añadió a `frontend-v2/index.html` el panel **Comparar proveedores**, accesible por navegación. Se puede introducir de forma manual el nombre de **dos o tres proveedores distintos** para un período. `frontend-v2/js/comparar-proveedores.js` normaliza la razón social (acentos, mayúsculas y espacios), calcula SHA-256 y descarga **solo un agregado por proveedor y entidad** desde `data/perfiles/AAAA-MM/{ofertas,resultados,ordenescompra}/xx.json`. No carga archivos históricos ni accede a Google Sheets.

Se presentan para cada entidad tres indicadores: número de registros, registros con monto informado y suma de montos. Se informa claramente que los resultados de entidades diferentes no deben sumarse como transacciones únicas ni adjudicaciones verificadas.

## Límites
- No existe aún buscador de autocompletado de razones sociales: el usuario debe escribir el nombre tal como aparece en el registro, excepto cambios de acentos/caso/espacios.
- Variantes ortográficas y cambios de razón social pueden quedar en perfiles distintos.
- Un proveedor sin registros para la entidad seleccionada aparece como «Sin registros identificados», no implica que nunca haya trabajado con organismos públicos.
- No se infieren montos contratados, pagos ni adjudicaciones finales desde simples registros.
- El comparador no depende de la entidad escogida en el selector; sí del mes seleccionado.

## Evidencia
Archivos: `frontend-v2/index.html`, `frontend-v2/js/comparar-proveedores.js`, `frontend-v2/css/styles.css`.
Workflow: https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39665354319. El resultado debe confirmarse en GitHub Actions. Pruebas manuales de nombres reales y maquetación quedan pendientes. V1, Sheets, ETL y fragmentos publicados permanecen intactos.


## Mejora: selección asistida de razones sociales — 21-10-2026
Se revisó README, índice documental, decisiones y esta documentación antes de intervenir. Se incorporó `scripts/generar_autocompletado_proveedores_v2.py`, que recorre **únicamente los agregados públicos ya publicados** de Ofertas, Resultados y Órdenes de compra; fusiona proveedores por nombre normalizado, construye archivos de sugerencias por las dos primeras letras y publica un metadato mensual. No lee fragmentos históricos ni fuentes privadas.

Se añadieron campos con `datalist` al comparador y se conectó `frontend-v2/js/comparar-proveedores.js` para cargar sugerencias a demanda según período y prefijo, con debounce de 200 ms, máximo 40 opciones y caché de 12 grupos. La entrada manual sigue siendo posible. Solo se sugieren coincidencias al **inicio** de la razón social normalizada; no se resuelven RUT ni alias.

Workflow `.github/workflows/publicar-autocompletado-v2.yml`, ejecución [#39665786022](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39665786022), iniciada; verificar conclusión y existencia de metadatos de todos los meses antes de dar por publicada la función. La validación visual de las sugerencias en el navegador queda pendiente.


## Publicación confirmada de selección asistida
Primera ejecución [#39665786022](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39665786022) falló por nombres físicos de prefijo con `/`. Se sustituyó el nombre de archivo por los dos primeros caracteres hexadecimales del SHA-256 del prefijo, de forma coherente en Python y JavaScript. La segunda ejecución [#39665979872](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39665979872) concluyó con **success**.

Los cinco `meta.json` fueron verificados directamente en GitHub: junio 32.328 proveedores (232 grupos), julio 32.237 (232), agosto 33.097 (234), septiembre 32.767 (229) y octubre 18.183 (218). Estos recuentos son nombres normalizados, no RUT únicos. Publicación y sintaxis verificadas; la interacción con `datalist` queda por validar visualmente en el navegador. Entrada manual conservada. V1, ETL, Sheets y fragmentos históricos intactos.


## Incidencia visual del autocompletado «so» — 21-10-2026
El usuario reportó que el comparador mostraba «Las sugerencias no están publicadas para este período» al ingresar `so`. La hipótesis de ausencia de índices fue descartada consultando directamente los archivos `frontend-v2/data/autocompletar/2026-MM/a1.json` en GitHub: el prefijo `so` corresponde a SHA-256 `a1`; existen listas con 1.806, 1.779, 1.869, 1.840 y 918 nombres coincidentes, respectivamente, para junio a octubre. Todos los `meta.json` anteriores también estaban publicados. Por tanto, el mensaje era falso/mal diagnosticado: el código lo mostraba ante cualquier HTTP 404 del primer origen GitHub Pages, sin consultar el respaldo público.

Se actualizó `frontend-v2/js/comparar-proveedores.js` (commit `b024fdaa`) para intentar Pages y, ante fallo, usar como respaldo el archivo de GitHub raw en `main` con `cache:'no-store'`; el mensaje de error ahora declara fallo de acceso en vez de falta de publicación. El catálogo y los nombres no se alteraron; tampoco V1, Sheets ni ETL. **Pendiente:** comprobación en navegador de respuesta efectiva tras propagación del frontend, pues no se obtuvo verificación HTTP directa de GitHub Pages desde el entorno.
