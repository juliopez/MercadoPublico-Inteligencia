# Frontend MER v2 — desarrollo independiente

**Inicio:** 2026-10-21. **Estado:** base visual y lector por período publicados en código, **sin datos MER v2 exportados y sin despliegue independiente validado**.

## Reglas obligatorias de convivencia

1. La v1 sigue en `/index.html`; conserva su publicación, experiencia de usuario y datos `/data/`. **No alterar** `index.html`, `data/observatorio.json`, `data/partes/` ni workflows de publicación v1 durante la construcción v2.
2. Toda la v2 está en `/frontend-v2/`, incluidos HTML, CSS, JS y `data/catalogo-publico.json`. Se prepararán fragmentos en `frontend-v2/data/partes/{entidad}/{AAAA-MM}/{archivo}.json`, separados de v1.
3. No publicar identificadores internos ni información privada de Google Sheets. Solo extractos explícitos de entidades públicas; seis tablas MER v2 sustentan modelo, cuatro son visibles inicialmente.
4. El catálogo v2 comienza vacío intencionadamente: muestra «aún no publicados» en lugar de inventar cifras o consumir por error la v1.
5. No desplegar nueva interfaz como reemplazo principal hasta completar contrato, publicación y validación en paralelo. El vínculo a v1 permite comparación funcional.

## Inventario de funcionalidades a preservar desde v1

| Capacidad v1 | Estado previsto en v2 |
|---|---|
| Búsqueda y filtros de procesos | Base de consulta incorporada; filtros especializados pendientes |
| Detalle de licitación y enlace al portal | Pendiente |
| Ofertas asociadas y trazabilidad de resultados | Pendiente |
| Comparar empresas | Pendiente |
| Perfil de organismo comprador | Pendiente |
| Perfil de proveedor/empresa | Pendiente |
| Órdenes de compra | Base de entidad y tabla incorporada; filtros y detalle pendientes |
| Mis favoritos | Pendiente |
| Exportación CSV | Pendiente |
| Indicadores, recuentos y fecha de actualización | Base incorporada, depende de extractos v2 |
| Paginación | 25 registros por página en prototipo v2 |
| Seguridad de rutas de fragmentos | Restricción a carpeta y patrón por período/entidad |

## Contrato inicial de datos v2

`frontend-v2/data/catalogo-publico.json`:
```json
{
  "version":"2.0",
  "fecha_publicacion":null,
  "fuente":"MER v2 — extractos públicos por período",
  "periodos":[
    {
      "periodo":"2026-06",
      "tipo":"historico",
      "conteos":{"procesos":0,"ofertas":0,"resultados":0,"ordenescompra":0},
      "partes":{"procesos":["data/partes/procesos/2026-06/0001.json"],"ofertas":[],"resultados":[],"ordenescompra":[]}
    }
  ]
}
```
**Ejemplo estructural, no datos reales**. No incorporar períodos sin archivos y recuentos verificados. El lector hace peticiones **solo al seleccionar** período y entidad, comprueba rutas y recuentos, limita vista a 25 filas, y no usa credenciales ni consulta Google Sheets desde el navegador. La primera implementación todavía acumula los fragmentos de la **entidad seleccionada** en memoria; deberá paginar/buscar mediante índices antes de publicar grandes volúmenes.

## Continuidad del Plan Maestro

- Tarea 14: preparar exportador multiperíodo desde catálogo, lectura privada de Sheets y validaciones.
- Tarea 15: publicar los extractos **separados de v1** y un manifiesto v2.
- Tarea 16: consulta por mes/período y relaciones.
- Tarea 17: rendimiento con índices/carga parcial real para millones de filas.
- Tareas 19/21: evaluación funcional y despliegue paralelo, nunca sustitución no aprobada.

**No interpretar el prototipo como un frontend funcional con datos reales.** La versión v1 sigue siendo la referencia operativa y la fuente de requisitos de experiencia de usuario.
