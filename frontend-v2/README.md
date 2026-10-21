# Frontend MER v2 — desarrollo independiente

**Inicio:** 2026-10-21. **Estado:** base visual y lector por período preparados. **Primera exportación real de octubre publicada en el repositorio** y verificada por GitHub Actions; **sitio v2 todavía sin despliegue independiente ni prueba de navegador**.

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
| Detalle de licitación y enlace al portal | Ficha básica de registro habilitada; enlace oficial para procesos; relaciones pendientes |
| Ofertas asociadas y trazabilidad de resultados | Pendiente |
| Comparar empresas | Pendiente |
| Perfil de organismo comprador | Pendiente |
| Perfil de proveedor/empresa | Pendiente |
| Órdenes de compra | Tabla y ficha de detalle básico habilitadas; relaciones y filtros avanzados pendientes |
| Mis favoritos | Pendiente |
| Exportación CSV | Pendiente |
| Indicadores, recuentos y fecha de actualización | Base incorporada, depende de extractos v2 |
| Paginación | **10 registros por página en las cuatro entidades** |
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
**Ejemplo estructural, no datos reales**. No incorporar períodos sin archivos y recuentos verificados. El lector hace peticiones **solo al seleccionar** período y entidad, comprueba rutas y recuentos, limita vista a 10 filas, y no usa credenciales ni consulta Google Sheets desde el navegador. La primera implementación todavía acumula los fragmentos de la **entidad seleccionada** en memoria; deberá paginar/buscar mediante índices antes de publicar grandes volúmenes.

## Continuidad del Plan Maestro

- Tarea 14: preparar exportador multiperíodo desde catálogo, lectura privada de Sheets y validaciones.
- Tarea 15: publicar los extractos **separados de v1** y un manifiesto v2.
- Tarea 16: consulta por mes/período y relaciones.
- Tarea 17: rendimiento con índices/carga parcial real para millones de filas.
- Tareas 19/21: evaluación funcional y despliegue paralelo, nunca sustitución no aprobada.

**No interpretar el prototipo como un frontend funcional con datos reales.** La versión v1 sigue siendo la referencia operativa y la fuente de requisitos de experiencia de usuario.

## Primera publicación real — 21/10/2026

Exportación aislada usando `scripts/exportar_frontend_v2.py` y [workflow de publicación v2](../.github/workflows/publicar-frontend-v2.yml), confirmada en [ejecución exitosa](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39639320943). **Período 2026-10:** Procesos **1.558**, Ofertas **0**, Resultados **0**, Órdenes de Compra **91.070**. Los ceros son ausencia efectiva en las pestañas del operativo de octubre a la fecha, no errores ni valores históricos extrapolados. El catálogo de publicación está en [`data/catalogo-publico.json`](data/catalogo-publico.json); los fragmentos dentro de `data/partes/`.

Primer intento de cuatro entidades falló por cuota **429 de lecturas Google Sheets por minuto**. Se ajustó a bloques de 5.000 filas y reintentos con espera, y la segunda ejecución **terminó correctamente**. La v1 continúa en `/index.html` y `/data/` sin cambios por estos exportadores.

**Pendiente antes de declarar front v2 operativo:** despliegue independiente/Pages, navegación real y carga selectiva de grandes volúmenes (el lector actual descarga todos los fragmentos de la entidad elegida). Los históricos junio–septiembre aún no han sido exportados al catálogo v2. Ejecutar manualmente el workflow por mes y entidad, verificando la cobertura antes de ampliar. La publicación actual de datos en GitHub **no implica que la web v2 ya esté desplegada**.

## Vista previa web — actualización del 21/10/2026

Se creó el flujo [`preview-frontend-v2.yml`](../.github/workflows/preview-frontend-v2.yml): valida el manifiesto y todos los fragmentos referenciados, empaqueta el repositorio con la v1 en la raíz y despliega a GitHub Pages, exponiendo la v2 en la ruta `/frontend-v2/`. **La ruta no reemplaza la v1.**

Primera ejecución: [GitHub Actions #39639890184](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39639890184). En la revisión inicial quedó en estado `waiting` por autorización del entorno protegido `github-pages`; la API muestra despliegue pendiente y `current_user_can_approve=false`. **No atribuir éxito hasta que el workflow termine y se compruebe la URL en navegador.** No desactivar ni eludir aprobaciones del entorno para acelerar la publicación.

URL **prevista**, no verificada todavía: `https://juliopez.github.io/MercadoPublico-Inteligencia/frontend-v2/`. Cuando la aprobación se resuelva, verificar catálogo 2026-10, Procesos 1.558, Ofertas 0, Resultados 0 y OC 91.070, paginación 10/25, y conservar funcionamiento del enlace a v1.

## Actualización de interfaz — navegación de 10 registros y detalle (21/10/2026)

- Los resultados visibles pasan a **10 por página** para Procesos, Ofertas, Resultados y Órdenes de Compra; es paginación de interfaz, **no implica** descargar solo 10 registros desde la red. La mejora de carga por índices sigue pendiente.
- La acción **Ver detalle** presenta una ficha con las columnas públicas del registro exportado, en el mismo sitio. Para Procesos incorpora vínculo al detalle oficial de Mercado Público con HTTPS y dominio permitido; si no existe URL compatible se construye la ficha desde el código cuando cumple el formato.
- No es todavía equivalente a la ficha completa de v1: **ofertas relacionadas, resultados vinculados, perfiles, comparación de empresas, favoritos y CSV siguen pendientes**. No declarar migración completa de la v1.
- El código y los documentos de producción v1 siguen intactos. Validar la interacción real en navegador tras despliegue de Pages.

## Prueba de históricos MER v2 — junio a septiembre de 2026

**Objetivo acordado:** incorporar cuatro meses históricos **sin modificar las seis tablas de las Google Sheets originales, ni archivos de datos ni frontend de v1**. El volumen es grande: suman **3.197.115 filas en las seis entidades**, según auditorías previas. Por eso la primera prueba se ejecuta sobre **Procesos completos de cada mes** antes de ampliar a Ofertas/Resultados/OC y medir rendimiento real.

**Control de permisos:** ejecución inicial de [GitHub Actions 39641670544](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39641670544) devolvió 403 por no compartir los históricos con la identidad de servicio. Se concedió permiso **reader**, exclusivamente, a `observatorio-mercadopublico@mercadopublico-inteligencia.iam.gserviceaccount.com` en las cuatro Sheets. No se alteraron sus datos. En el segundo intento se leyeron todos los Procesos de junio (80.898), julio (80.996) y agosto (83.937), pero la lectura de la cabecera de septiembre recibió 429 por cuota de Sheets. Al ser una publicación transaccional al final del job, ese intento **no incorporó esos registros a GitHub**. Se agregó reintento también a la lectura de cabeceras y se inició una nueva ejecución.

**Advertencia:** 10 filas por página es una paginación visual; el lector v2 aún descarga todos los fragmentos de la entidad seleccionada. La carga completa de Ofertas (aproximadamente 1,7 millones de registros entre junio y septiembre) requiere índice/búsqueda selectiva y evaluación del tamaño final antes de publicar. No declarar históricas todas las entidades publicadas si el catálogo solo refleja Procesos.

## Resultado confirmado del piloto histórico — 21/10/2026

La exportación de la entidad **Procesos** concluyó exitosamente para los cuatro históricos, [run GitHub Actions #39642284420, intento posterior](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39642284420):

| Período | Procesos publicados | Fragmentos |
|---|---:|---:|
| 2026-06 | 80.898 | 81 |
| 2026-07 | 80.996 | 81 |
| 2026-08 | 83.937 | 84 |
| 2026-09 | 79.376 | 80 |
| **Total** | **325.207** | **326** |

Los documentos se obtuvieron directamente de las cuatro hojas MER v2 con **permiso reader** de la cuenta de servicio; Sheets históricos y datos v1 permanecieron sin escrituras. [Catálogo publicado](data/catalogo-publico.json). Las otras tres entidades visibles de esos meses **no están publicadas todavía**, y el lector actual acumula todos los fragmentos de un período y entidad en la memoria del navegador. El despliegue Pages tras cada cambio del catálogo está incorporado al flujo [preview](../.github/workflows/preview-frontend-v2.yml). Antes de exportar Ofertas a gran escala se debe abordar rendimiento y estrategia de entrega; no interpretar la paginación de 10 filas como paginación de red.
