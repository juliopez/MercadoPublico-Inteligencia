# Instalación y reproducción por niveles

Esta guía distingue **visualizar el frontend**, **conectar datos propios** y **operar automáticamente**. No existe una instalación integral de un solo comando verificada para un entorno ajeno.

## Nivel 1: clonar y explorar el frontend

Requisitos: Git, Python 3 y navegador moderno.

```bash
git clone https://github.com/juliopez/MercadoPublico-Inteligencia.git
cd MercadoPublico-Inteligencia
python3 -m http.server 8000
```

Abrir `http://localhost:8000/`. El servidor HTTP local es importante porque el frontend carga JSON mediante `fetch`; abrir `index.html` como archivo local puede bloquear esas solicitudes. Los datos públicos versionados se encuentran bajo `frontend-v2/data/`. No se necesita acceso a las hojas privadas para este nivel.

**Verificación mínima:** cargar la portada, seleccionar un período del catálogo, abrir un registro y probar la búsqueda transversal. Si falla, inspeccionar la consola y las rutas HTTP de los JSON. Este procedimiento se deriva de la arquitectura estática; **no se presenta como prueba recién ejecutada en un equipo limpio**.

## Nivel 2: utilizar fuentes y almacenamiento propios

1. Crear almacenamiento privado con las seis entidades MER y decidir cómo representar el período.
2. Revisar [modelo de datos](MODELO_DATOS.md) y [arquitectura](ARQUITECTURA.md).
3. Crear **su propio** catálogo de fuentes, carpetas y credenciales; no reutilizar IDs de Drive/Sheets del proyecto original.
4. Adaptar los scripts de ingestión y exportación a su proveedor de almacenamiento.
5. Generar catálogo, fragmentos JSON e índices coherentes con los contratos de `frontend-v2/data/`.
6. Validar conteos, claves, integridad de archivos y ausencia de información privada antes de publicar.

**Importante:** `config/catalogo_sheets.json` describe recursos de la instalación de referencia y no es una plantilla portable lista para ejecutar. Tampoco se entregan credenciales productivas. Ver [configuración](CONFIGURACION.md).

## Nivel 3: automatización y despliegue

1. Preparar Ubuntu u otro planificador y sus secretos.
2. Configurar tareas separadas para ETL diario, API incremental, rotación y conciliación.
3. Configurar workflows de generación/publicación e índices con permisos mínimos.
4. Establecer un repositorio y hosting propios; comprobar las rutas relativas de la aplicación.
5. Validar ejecuciones manuales controladas antes de activar horarios.
6. Comprobar reintentos, idempotencia, fallas de red, límites API, bloqueos y reversión.
7. Probar el **ciclo mensual completo** en entorno de pruebas antes de considerarlo autónomo.

La referencia de ejecución y límites está en [automatización](AUTOMATIZACION.md) y en los runbooks originales.

## Criterios de aceptación de una instalación nueva

- Frontend responde por HTTP y lee el catálogo.
- Datos públicos no exponen secretos ni IDs privados sensibles.
- Conteos del catálogo concuerdan con fragmentos e índices publicados.
- Consultas por código y perfiles devuelven resultados reproducibles.
- Cada tarea tiene logs, checkpoint y mecanismo de recuperación.
- Rotación y conciliación se verifican con evidencia real, no solo con una configuración habilitada.
