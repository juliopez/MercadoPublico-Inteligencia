# Lote de cinco observaciones visuales — frontend V2
Fecha: 21-10-2026.

## Alcance aprobado
El usuario terminó la revisión visual y autorizó ejecutar las cinco observaciones en un solo lote. Se leyeron README, índice documental, decisiones técnicas y archivos reales de V2 antes de intervenir. La auditoría integral de prioridad 5 del plan previo sigue siendo una tarea distinta: este lote solo resuelve las cinco observaciones visuales.

1. **Fecha de publicación:** el texto ISO con UTC se transforma con `Intl.DateTimeFormat('es-CL',{timeZone:'America/Santiago',dateStyle:'long',timeStyle:'short'})`. Se ajustó el tamaño y quiebre del indicador para evitar desbordes.
2. **Evolución mensual:** además de las barras existentes se agregaron cantidad total de registros de la entidad, promedio mensual del período junio–septiembre 2026, variación del último mes completo y etiqueta de mes reciente. Cada barra exhibe variación respecto al mes anterior. Los valores proceden de `catalogo-publico.json`, no de sumas de distintas entidades; octubre 2026 es mes parcial y no se considera en el promedio de meses completos.
3. **Ordenamiento:** encabezados clicables con sentido ascendente/descendente en la tabla local (todos los registros filtrados del bloque antes de paginar), perfil contextual (registros cargados del actor antes de truncar a 25), tablas de registros relacionados (conjunto obtenido para el proceso antes de paginar), comparador (filas de indicadores) y resultados globales. **Límite explícito:** el orden de búsqueda global se aplica a las coincidencias *ya verificadas por el navegador*, no al universo total de coincidencias futuras en fragmentos aún no descargados. No se sacrifica carga progresiva ni se afirma orden global total.
4. **Sección V1 obsoleta:** eliminada del HTML sin modificar la V1.
5. **Landing:** añadidos encabezados/separadores de Exploración, Análisis, Profundización/Comparación y Seguimiento; se ordenó Comparar proveedores antes de Favoritos para respetar dependencias.

## Verificación y protección
`frontend-v2/index.html`, `frontend-v2/js/app.js`, `frontend-v2/js/busqueda-global.js`, `frontend-v2/js/comparar-proveedores.js`, `frontend-v2/css/styles.css` y `.github/workflows/validar-ajustes-landing-v2.yml`.

GitHub Actions [#39674719331](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39674719331): `success` confirmado. Cuatro módulos validados sintácticamente con Node y verificación de elementos de las cinco mejoras. **La revisión visual en navegador sigue pendiente del usuario.** No hubo cambios en V1, Sheets, ETL, históricos ni índices publicados.

## Prueba visual sugerida
Actualizar forzosamente V2, comprobar fecha con horario de Chile, cuatro indicadores y variación en barras por entidad, encabezados ascendentes/descendentes en consultas y tablas secundarias, desaparición del bloque V1 y separadores de secciones. El orden en búsquedas globales debe leerse como orden de resultados verificados hasta ese momento.
