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
