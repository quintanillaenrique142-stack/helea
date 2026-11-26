# HELÉA – sitio web (catálogo)

Sitio estático, hecho para celular y computadora. Se publica gratis con GitHub Pages desde la carpeta `docs/`.

## Cómo agregar o cambiar una pieza
1. Edita `src/catalog.json` (nombre, colección, tipo, precio).
   Campos opcionales: `description`, `material`, `size`, `care`, `variants`, `"sold_out": true`.
2. Pon la foto cuadrada en `docs/assets/img/<slug>.jpg`.
3. Ejecuta `python3 src/build.py` y sube los cambios.

`python3 src/build.py --draft` muestra en amarillo los datos que faltan.

Dominio: heleajewelry.com (Porkbun). `docs/CNAME` y `base_url` ya apuntan a él.

## Colección pasada (Summer) oculta
Las piezas de la Summer Collection siguen en `src/catalog.json` (marcadas `"archived": true`) y sus fotos en `src/archive-img/`.
Para volver a mostrarla: pon `"show_past": true` en `src/catalog.json` y ejecuta `python3 src/build.py`.
