# Mejoras integrales de experiencia de usuario — Observatorio V2
**Fecha:** 21 de octubre de 2026. **Intervención autorizada:** implementar las siete propuestas de experiencia de usuario más las dos observaciones del usuario, en conjunto. **Alcance:** solo frontend-v2 y pruebas; no V1, Google Sheets, ETL ni fragmentos históricos.

## Documentación consultada
Antes de intervenir: README, índice documental, decisiones técnicas vigentes, registro de ajustes visuales y archivos reales HTML, CSS y módulos JavaScript de V2. Se conservan la carga selectiva por fragmentos, la paginación de 10 y la búsqueda indexada.

## Nueve intervenciones
1. **Entrada de búsqueda simplificada:** selección central de período y entidad, botón «Buscar en todo el período» y búsqueda global marcada como recomendada. La consulta local permanece en panel desplegable «Exploración por bloques (opción avanzada)». No se eliminó ninguna función.
2. **Filtros contextuales:** solo se habilitan los aplicables a la entidad (Procesos: estado y modalidad; Ofertas: seleccionado; Órdenes de compra: estado y tipo). La verificación interna de Resultados no se ofrece como filtro visible. Las búsquedas globales siguen necesitando palabra o código; no hay índice autónomo por facetas.
3. **Navegación entre registros:** códigos principales y relacionados son controles navegables hacia la consulta global indexada de la entidad correspondiente. La ficha original de Procesos conserva sus grupos de registros vinculados; los códigos OC y de procesos se distinguen y no se genera artificialmente una URL oficial de licitación para Compra Ágil. Si un código está publicado en otro mes, hay que seleccionar ese período.
4. **Estados de carga:** indicador de progreso de referencias examinadas y mensajes de avance para búsqueda global. Representa fracción de *candidatos indexados examinados*, no progreso de todo el histórico.
5. **Fichas jerarquizadas:** resumen visual con campos más relevantes por entidad (código, nombre o proveedor, estado y montos) y sección «Mostrar todos los campos del registro» desplegable. Se conservan vínculos y relaciones.
6. **Conservar contexto:** botón «Volver a la consulta anterior» cuando el usuario navega a otro código; restaura mes, entidad, bloque y filtros básicos. No equivale a historial persistente del navegador.
7. **Accesibilidad y móviles:** acceso «Saltar a la consulta», foco visible, encabezados claros, resumen desplegable nativo, progreso etiquetado y adaptación responsiva de navegación, tablas y controles. No se declara certificación WCAG sin auditoría especializada.
8. **CLP consistente:** reconocimiento de campos monetarios y formato con Intl.NumberFormat en tablas locales, globales, tablas relacionadas, fichas y perfiles; el comparador conserva su formato CLP. «No informado» se mantiene para valores vacíos. No se alteran los valores originales en JSON. Los CSV mantienen los valores de origen para reutilización numérica.
9. **Códigos navegables:** enlaces internos por código desde celdas, perfiles, fichas y registros vinculados. Se acepta introducir un código alfanumérico completo con guiones, incluidos segmentos cortos, en la búsqueda global. Para la ficha oficial solo se usan URLs presentes o la ruta conocida de licitación cuando el patrón es compatible; no se inventa una ficha para COT u OC.

## Verificación técnica
- Workflow: [Validar mejoras UX integrales V2 — ejecución #39677792920](https://github.com/juliopez/MercadoPublico-Inteligencia/actions/runs/39677792920), estado **success** confirmado.
- Cuatro módulos JavaScript con sintaxis válida.
- Pruebas automatizadas de formato CLP, estructura HTML, accesibilidad básica, vínculo de códigos, búsqueda por código completo, filtros de estado/modalidad y fichas.
- Primer intento detectó un error del propio test (identificador `detail-resumen` frente a `detalle-resumen`); se corrigió y la ejecución indicada terminó satisfactoriamente.

## Qué falta
Prueba visual/funcional en navegador de los nueve cambios con códigos reales de Procesos, Compra Ágil y OC; verificar un importe, un enlace y el regreso al contexto para cada tipo. La auditoría integral de prioridad 5 acordada anteriormente sigue **pendiente como tarea independiente**: no confundir estas pruebas automatizadas con una auditoría completa de rendimiento, accesibilidad o equivalencia funcional V1/V2.
