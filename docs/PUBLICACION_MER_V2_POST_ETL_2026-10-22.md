# Publicación incremental del MER operativo al frontend V2

**Estado 22/10/2026:** código publicado en GitHub. **No activado** en cron Ubuntu; requiere validación de exportación y sincronización del repositorio local. No se ha demostrado aún una publicación automática completa.

## Flujo
1. Ubuntu: cron integrado de las 16:00 actualiza MER mediante ZIP licitaciones y OC y concilia COT–OC.
2. Ubuntu: `scripts/exportar_mer_operativo_v2.py` lee el libro operativo, verifica cabeceras, PK y fragmentos; expone exclusivamente los campos públicos de Procesos y OrdenesCompra del mes.
3. Ubuntu: `scripts/ubuntu_publicar_v2_post_etl.sh --aplicar` exige sincronización exitosa del día, verifica Git limpio, publica los fragmentos y el catálogo. No exporta datos privados de Proveedores ni VinculosCOT_OC.
4. GitHub Actions: `.github/workflows/publicacion-v2-post-etl.yml`, agenda 17:00 Santiago, reconoce un commit del catálogo posterior a las 16:00 y solicita regeneración de analítica e índice de Procesos.

## Límites deliberados
- No escribe Sheets ni modifica históricos. No llena Ofertas ni Resultados sin fuente.
- No carga ZIP diario COT. No reprocesa junio–septiembre.
- El exportador no publica por sí mismo búsqueda global, perfiles, índices OC ni registro documental COT–OC; se requiere revisar los generadores existentes y coordinar su refresco antes de certificar toda la experiencia V2.
- El mecanismo de publicación NO fue insertado al cron actual porque aún falta prueba completa de exportación y comprobación de índices dependientes. La agenda GitHub se omite si no existe exportación nueva.
- Evitar usar una fecha de modificación del catálogo como única evidencia de éxito: cotejar SHA, conteos y el informe operativo.

## Prueba recomendada en Ubuntu, sin escritura ni commit
```bash
cd "$HOME/Julio Lopez/chilecompra/MercadoPublico-Inteligencia"
git pull --ff-only
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/mercadopublico/servicio-google.json"
bash scripts/ubuntu_publicar_v2_post_etl.sh
```
Tras la prueba revisar los conteos y la muestra de filas frente al MER. No activar publicación automática hasta reconciliar los índices derivados de V2.
