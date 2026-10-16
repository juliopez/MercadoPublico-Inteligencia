# Observatorio Mercado Público · Piloto v0.1

Dashboard estático inicial para estudiar ofertas de capacitación. **Los datos iniciales son ficticios**. No publicar información confidencial en un repositorio o sitio público.

## Uso local

Desde la carpeta del proyecto:

```bash
python3 -m http.server 8000
```

Abrir http://localhost:8000. También se puede importar un CSV local directamente desde el dashboard. Formato UTF-8, separador `;`, cabecera:

```text
codigo;tematica;organismo;proveedor;monto;resultado
```

`resultado` utiliza `Adjudicado` o `No seleccionado`; `monto` es entero en CLP. **Cada fila es una oferta**, no un proceso.

## Publicar en GitHub Pages

1. Crear repositorio GitHub (preferiblemente de prueba, sin datos sensibles).
2. Subir el contenido a la rama `main`.
3. Settings → Pages → Build and deployment → GitHub Actions.
4. Verificar el despliegue en Actions.

La carga del CSV por navegador es local y no envía el archivo a GitHub. Sin embargo, **cualquier CSV confirmado y subido al repositorio publicado será público**.

## Estado real de integración

- [x] Dashboard con filtros, métricas, gráficos y exportación CSV.
- [x] Formato de intercambio tabular y ejemplo totalmente ficticio.
- [x] Workflow de publicación en GitHub Pages.
- [ ] Conectar ticket oficial de ChileCompra en GitHub Actions Secrets.
- [ ] Validar esquema real de respuesta de API Compra Ágil v2 antes de mapearlo.
- [ ] Conectar Google Sheets y Looker Studio con credenciales seguras.
- [ ] Controlar duplicación de segundos llamados, fecha de extracción e histórico.

Fuentes: https://www.chilecompra.cl/api/ y https://docs.github.com/en/pages
