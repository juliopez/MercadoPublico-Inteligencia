# Observatorio de Inteligencia de Mercado Público · Chile

Plataforma para explorar y analizar **Procesos, Ofertas, Resultados y Órdenes de compra** de Mercado Público. Este README describe el **estado vigente**; los procedimientos y antecedentes están separados en la documentación especializada.

**Estado documental verificado: 30 de octubre de 2026.** [Bitácora actual de prueba API 400, iniciada 22:30](docs/BITACORA_PRUEBA_API_400_2026-10-30.md). La operación Ubuntu de las 16:00 fue comprobada el 30/10 mediante exportación, publicación V2 y supervisor de GitHub. La instalación de los nuevos servicios locales no se ha verificado.

**[Punto único de continuidad y estado real](docs/ESTADO_Y_CONTINUIDAD_2026-10-30.md).** [Instalación de rotación y conciliación](docs/INSTALACION_ROTACION_CONCILIACION_2026-10-30.md) · [API local — etapa siguiente](docs/CRON_LOCAL_API_COMPRA_AGIL_2026-10-30.md) · [Índice documental](docs/INDICE_DOCUMENTACION.md).

## Acceder

- **[Observatorio V2 — interfaz de consulta y análisis](https://juliopez.github.io/MercadoPublico-Inteligencia/frontend-v2/)**
- [Frontend V1 — versión anterior independiente](https://juliopez.github.io/MercadoPublico-Inteligencia/)
- [Manual de uso de V2](frontend-v2/README.md)
- [Índice completo de documentación](docs/INDICE_DOCUMENTACION.md)
- [Decisiones técnicas y restricciones](docs/DECISIONES_TECNICAS.md)

## Estado del sistema

| Componente | Estado y alcance |
|---|---|
| Frontend V2 | Implementado y publicado en `frontend-v2/`; **revisión visual de los últimos cambios en curso por el usuario** |
| Períodos públicos | Junio–octubre de 2026; octubre **parcial** |
| Datos disponibles | Cuatro entidades públicas: Procesos, Ofertas, Resultados y Órdenes de compra |
| Consulta | Primer bloque de hasta 1.000 filas; tablas paginadas de 10; búsqueda indexada por término/código entre todos los períodos publicados (o por un mes) |
| Analítica | Selección de mes, comparación entre meses, vistas de actividad, importes informados y actores destacados |
| Relaciones históricas | Fichas relacionadas entre **todos los meses publicados** mediante índices por código; no acceso a meses todavía no publicados |
| Herramientas | Fichas, perfiles, comparación de proveedores, favoritos del navegador y exportación CSV |
| Google Sheets MER | Datos privados; seis tablas internas, distintas de las cuatro entidades públicas |
| Auditoría integral V2 | **Pendiente** como actividad independiente de pruebas de CI y revisión visual |
| Cierre del mes de octubre | Primer cierre manual supervisado **previsto para el 10-11-2026**, sujeto a verificaciones y fuentes completas |

Los números y períodos vigentes se consultan siempre en el [catálogo público de V2](frontend-v2/data/catalogo-publico.json); no confiar en conteos copiados a documentación fechada.

## Cómo funciona V2

1. Seleccionar **mes** y **entidad**. «Mostrar registros del período» carga el primer bloque de forma directa y muestra páginas de 10.
2. Usar **Buscar en los históricos** para consultar todos los períodos publicados, con opción de limitar a un mes; la exploración por bloques permanece como opción avanzada.
3. Consultar el panel **Evolución mensual** para seleccionar, comparar períodos y alternar entre actividad, montos y actores.
4. Abrir una ficha y revisar su resumen, campos completos y **registros vinculados entre los meses publicados**.
5. Utilizar perfiles, comparación, favoritos y CSV cuando se requiera.

**Interpretación responsable:** la coincidencia por código no acredita adjudicación; una oferta, resultado o OC informada no equivale por sí sola a un contrato pagado. Las sumas CLP son descriptivas. Octubre 2026 sigue incompleto. El ordenamiento global afecta coincidencias verificadas, no resultados aún sin cargar.

## Arquitectura

```text
Fuentes ChileCompra / ZIP oficiales
   ↓
ETL y consolidación MER (Google Sheets privadas)
   ↓ exportación controlada
frontend-v2/data/catalogo-publico.json
   ├─ partes/                 registros públicos por fragmentos
   ├─ busqueda/               búsqueda indexada
   ├─ indices/                relaciones por código en Ofertas, Resultados y OC
   ├─ relaciones-procesos/    relaciones exactas de Procesos
   ├─ perfiles/ + autocompletar/
   └─ analitica/ + sugerencias/
   ↓
GitHub Pages V2 (sin acceso directo a Sheets)
```

**Reglas de protección:** no modificar V1 (`index.html`, `data/`) durante mejoras V2; no descargar el histórico completo al navegador; no eliminar JSON generados, workflows de datos, credenciales locales protegidas ni ramas de respaldo como parte de una limpieza editorial.

## Operación y mantenimiento

La operación diaria utiliza desde el 22/10/2026 el orquestador integrado Ubuntu de las 16:00, con ETL de licitaciones y OC, conciliación documental COT–OC y publicación condicionada en V2. La cadena Ubuntu → GitHub Actions → Pages quedó verificada el viernes 30/10; comprobar diariamente su continuidad mediante los logs y supervisión. La rotación operativa y la preparación recuperable de conciliación están implementadas en código y con temporizadores preparados, **instalados y con rotación octubre→noviembre ejecutada y verificada el 30/10; cierre histórico oficial todavía pendiente**. Octubre no se ha archivado definitivamente; la conciliación oficial sigue requiriendo tres ZIP, respaldos, auditoría y aprobación. No alterar el cron diario.

- [Runbook del cierre de octubre](docs/RUNBOOK_CIERRE_2026_10.md)
- [Procedimiento general de cierre mensual](docs/PROCEDIMIENTO_CIERRE_MENSUAL.md)
- [ETL operativo Ubuntu](docs/UBUNTU_ETL_DOS_FUENTES.md)
- [Modelo de consolidación MER v2](docs/CONSOLIDADOR_MER_V2.md)
- [Mantenimiento y limpieza segura de GitHub](docs/MANTENIMIENTO_REPOSITORIO_2026-10-21.md)

## Desarrollo, pruebas y documentación

- Código frontend: `frontend-v2/`. Scripts de datos: `scripts/`. Pruebas: `tests/`. Workflows: `.github/workflows/`.
- [Manual técnico V2](frontend-v2/README.md) y [analítica con relaciones multimes](docs/ANALITICA_INTERACTIVA_RELACIONES_HISTORICAS_V2_2026-10-21.md).
- **No confundir niveles de evidencia:** implementado, probado en GitHub Actions, revisado visualmente y ejecutado en datos operativos son estados diferentes.
- [Documentación por temas](docs/INDICE_DOCUMENTACION.md) y [decisiones técnicas](docs/DECISIONES_TECNICAS.md).

**Continuidad:** antes de intervenir leer este README → índice → decisiones → documento específico → código real. Mantener la historia técnica en documentos especializados o [README legado](docs/historial/README_LEGADO_2026-10-21.md), no agregar bitácoras al README principal.

**Últimas mejoras V2:** [búsqueda transversal multimes](docs/BUSQUEDA_TRANSVERSAL_MULTIMES_V2_2026-10-21.md) con detalle navegable, [participantes históricos](docs/PARTICIPANTES_HISTORICOS_V2_2026-10-21.md) y [vista unificada de OC](docs/VISTA_UNIFICADA_OC_FRONTEND_V2_2026-10-21.md). Verificación visual de funciones puntuales en curso; no equivale a auditoría integral.

**Antecedentes operativos fechados (no son estado vigente):** [cierre técnico y validación del 22/10](docs/CIERRE_OPERATIVO_Y_VALIDACION_2026-10-22.md), [publicación V2](docs/PUBLICACION_MER_V2_POST_ETL_2026-10-22.md) y [cron integrado](docs/CRON_INTEGRADO_UBUNTU_2026-10-22.md). El [plan anterior](docs/PLAN_MEJORAS_CRON_1600_2026-10-21.md) se conserva como antecedente histórico. La API local realizó una carga productiva de hasta 100 (99 procesos nuevos). La siguiente prueba manual de hasta 400 comenzó, según informó el usuario, el 30/10 a las 22:30; **resultado y duración pendientes**. Véase la bitácora de prueba de 400 antes de continuar. Ver [guía API local](docs/CRON_LOCAL_API_COMPRA_AGIL_2026-10-30.md).
