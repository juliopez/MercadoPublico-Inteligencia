# Navegación desde participación histórica de organismos — V2

**Estado:** corrección publicada en `main`; validación visual aún pendiente.

## Diagnóstico

En `frontend-v2/js/participantes-historicos.js`, los botones `Examinar AAAA-MM` usan el nombre completo del participante como búsqueda global. El buscador global (`frontend-v2/js/busqueda-global.js`) rechaza consultas con términos menores de tres caracteres, salvo códigos completos. Los nombres de organismos suelen incluir preposiciones o artículos (por ejemplo `de`, `la`, `el`), por lo que la navegación puede resultar bloqueada aunque haya registros en índices.

## Corrección acotada

Para `participante-tipo=organismo`, el botón `Examinar` omite términos de menos de tres caracteres al trasladar el nombre a `busqueda-global-texto`; selecciona el período, establece entidad `procesos`, limpia filtros y ejecuta búsqueda global. Para `proveedor` mantiene el funcionamiento anterior.

**Limitación:** el traspaso utiliza una búsqueda por palabras de tres o más caracteres; los resultados finales son coincidencias de la consulta y podrían incluir más de un organismo si los términos no son únicos. No sustituye una búsqueda exacta por identificador institucional. No se han modificado datos, índices, histórico, ETL ni backend.

## Validación

Verificado en código: `participante-tipo` usa los valores `proveedor` y `organismo`; el buscador global indexa `organismo_comprador` en la entidad `procesos`. Prueba visual del botón `Examinar` para organismo pendiente. Caso sugerido: `SERVICIO LOCAL DE EDUCACIÓN PÚBLICA DE HUASCO`.
