# Configuración para una instalación independiente

## Qué configurar

| Área | Elementos | Recomendación |
|---|---|---|
| Fuentes | ZIP oficiales, acceso API y períodos | Verificar formatos y condiciones vigentes de ChileCompra |
| Almacenamiento | Hojas MER, carpetas de Drive o base alternativa | Usar recursos **propios** y permisos mínimos |
| Identidad | Cuenta de servicio Google, tokens GitHub | Secretos fuera del repositorio y de Pages |
| Ejecución | Python, dependencias de scripts, Ubuntu/systemd | Documentar versiones efectivas del entorno |
| Publicación | Rama, permisos Actions, Pages, rutas del frontend | Comprobar que catálogo y fragmentos coincidan |
| Operación | Horarios Chile, reintentos, checkpoints y logs | Validar `America/Santiago` y cambios de hora |

Los nombres exactos de secretos y variables se deben extraer del workflow o script concreto que se despliegue; **no inventar valores genéricos ni copiar los de producción**. El archivo `config/catalogo_sheets.json` contiene identificadores de la instancia original y debe tratarse como **referencia estructural**, no como configuración reutilizable.

## Separación de ambientes

Mantener desarrollo/pruebas separados de producción, usar datos sintéticos o copias autorizadas y nunca escribir sobre hojas de la instancia original desde un clon. Comprobar permisos de lectura/escritura y política de respaldo antes de habilitar timers.
