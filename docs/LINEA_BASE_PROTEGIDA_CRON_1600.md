# LÍNEA BASE PROTEGIDA — CRON Ubuntu de las 16:00

> **ESTADO: VALIDADO OPERATIVAMENTE — NO MODIFICAR COMO PARTE DE OTROS DESARROLLOS.**
>
> Esta decisión expresa del responsable del proyecto protege la cadena diaria existente. Ninguna mejora de la API nocturna, cambio de mes, refactorización, limpieza de GitHub o nuevo workflow debe alterar su configuración, horario, scripts, contratos de datos, bloqueos o despliegue. Una intervención excepcional requiere autorización específica, respaldo, plan de pruebas y reversión.

## Alcance y evidencia

Ejecución prevista lunes a viernes a las **16:00 America/Santiago**, desde Ubuntu. La cadena Ubuntu → MER Google Sheets → GitHub Actions → Pages se verificó el **30/10/2026** mediante exportación local y workflows de derivados/supervisión exitosos (véase [estado operativo](ESTADO_Y_CONTINUIDAD_2026-10-30.md)). El usuario ratificó expresamente esta cadena como **totalmente validada**. No implica que todos los días futuros estén garantizados sin fallas externas; es una línea base de cambios protegida, no una promesa de disponibilidad.

## Flujos protegidos y ejecutores

| Etapa | Responsabilidad | Archivos principales |
|---|---|---|
| 1. Arranque y preflight | Día/hora, credenciales, entorno, catálogo operativo, bloqueos | `scripts/ubuntu_cron_integrado.sh`, `scripts/ubuntu_cron_etl.sh` |
| 2. ETL de fuentes | Descargar, procesar e importar licitaciones y OC | `scripts/ubuntu_etl_dos_fuentes.sh`, `scripts/etl_zip_dos_fuentes.py` |
| 3. Persistencia y evidencia | MER privado y estado de sincronización | `scripts/registrar_sincronizacion.py`, `salida_operativa/estado_sincronizacion.json` local |
| 4. Conciliación documental | OC incremental, SHA256 de ZIP, conciliación COT–OC y control de duplicados | `scripts/descargar_oc_incremental.py`, `scripts/etl_conciliacion_cot_oc.py` |
| 5. Exportación pública | Catálogo/partes JSON y vínculos documentales, commit y push | `scripts/ubuntu_publicar_v2_post_etl.sh`, `scripts/exportar_mer_operativo_v2.py`, `scripts/exportar_vinculos_documentales_v2.py` |
| 6. Publicación y supervisión | Derivados, validación, Pages y vigilancia de actualidad | `.github/workflows/publicacion-v2-post-etl.yml`, `.github/workflows/preview-frontend-v2.yml`, `.github/workflows/verificar-publicacion-diaria-v2.yml` |

Dependencias y contratos también protegidos: `config/catalogo_sheets.json`, credenciales locales (nunca versionarlas), estado y hashes, controles de éxito del ETL, candados `flock` compartidos, orden de publicación y registros de auditoría. Los scripts auxiliares invocados por estos ejecutores se consideran protegidos en cuanto afecten este flujo.

## Reglas obligatorias de cambios

1. **No editar ni sustituir** ejecutores, horarios, timers/crontab, rutas, credenciales, contratos de entrada/salida, archivos de control o workflows identificados arriba por iniciativa de otra funcionalidad.
2. **No alterar el orden** ETL → verificación → conciliación → exportación → generación de derivados → despliegue, ni eliminar controles para acelerar procesos.
3. La **API Compra Ágil nocturna** debe permanecer independiente; coordinar escrituras mediante los bloqueos ya existentes **sin modificar** el cron de las 16:00.
4. La **rotación mensual** y la preparación/conciliación histórica son flujos separados; no deben introducir cambios colaterales en la línea base diaria.
5. **No borrar ni limpiar** logs locales, cola, respaldos, hojas MER, partes públicas, índices o workflows con impacto sobre esta cadena como parte de una limpieza editorial.
6. **Si fuera imprescindible intervenir**, documentar motivo, impacto, autorización expresa del usuario, copia/respaldo, comparación contra línea base, prueba controlada en entorno aislado, plan de reversión y validación de extremo a extremo antes de tocar producción.
7. Una falla externa debe diagnosticarse **sin asumir automáticamente que hay que reescribir** la cadena validada. Priorizar restablecimiento del componente fallido y preservación de los datos.

## Límites de esta declaración

- La cadena de las 16:00 **no incluye** la ingesta masiva de Compra Ágil por API nocturna, ni la rotación operativa de fin de mes ni la conciliación histórica oficial diferida.
- Se enumeran **10 scripts locales principales y 3 workflows directamente asociados**. Otros workflows del repositorio pueden compartir infraestructura, pero no son automáticamente parte del cron de las 16:00.
- Este documento registra una **decisión de gobierno de cambios**: no instala una protección técnica de rama ni impide que GitHub acepte un commit. Las protecciones técnicas adicionales requerirían una decisión separada.

## Regla de continuidad para chats futuros

**Antes de proponer cualquier modificación o automatización:** leer este archivo y tratar los componentes citados como inmutables salvo instrucción explícita. Desarrollar funciones nuevas mediante unidades, scripts o workflows separados; documentar sus dependencias y comprobar que no perturben la ejecución de las 16:00.

**Fuente:** [inventario y estado de continuidad](ESTADO_Y_CONTINUIDAD_2026-10-30.md) · [cron integrado original](CRON_INTEGRADO_UBUNTU_2026-10-22.md).
