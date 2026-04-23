#!/bin/bash
# Publicar manual básico en GitHub Pages
# Uso: bash publicar.sh  (desde la carpeta del repo)

set -e

echo "==> Generando notebooks..."
python generar_notebooks.py

echo "==> Commiteando notebooks actualizados..."
git add notebooks/
git diff --staged --quiet || git commit -m "Actualizar notebooks"

echo "==> Publicando sitio..."
mkdocs gh-deploy --force

echo "==> Publicando notebooks al repo..."
git push

echo "==> Listo: https://tomvalderrama.github.io/manual-introduccion-python-cientifico/"
