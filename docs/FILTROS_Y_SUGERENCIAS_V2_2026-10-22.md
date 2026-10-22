# Filtros y sugerencias de búsqueda — 22/10/2026

Se activa autocompletado de palabras clave en búsqueda transversal desde los índices públicos `data/sugerencias/{periodo}/{entidad}/{prefijo}.json`. Se agregan sugerencias de todos los meses publicados cuando la cobertura es «Todos»; en modo «Solo período seleccionado», se limita al mes. Se muestran hasta 30 propuestas con al menos dos letras.

Estado y Modalidad ahora son selectores desplegables con opción inicial «Todos». Los valores se agregan y deduplican de los `facetas.json` de los períodos de cobertura, sin consultas a la API ni a Google Sheets. La disponibilidad de filtros depende de la entidad: Resultados no tiene filtros de estado/modalidad aplicables; Ofertas solo tiene selección informada.

La lista de sugerencias es de ayuda; no cambia el contrato de búsqueda (tres caracteres mínimos salvo códigos completos). Los índices existentes, exportaciones, ETL y cron se preservan. Verificar en Pages que los selectores se cargan, que los cambios de entidad y período los refrescan y que el autocompletado funciona con cobertura multimes. No afirmar desplegado hasta comprobar el workflow Pages y el sitio público.
