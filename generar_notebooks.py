"""
Genera notebooks Jupyter (.ipynb) desde los capítulos del manual.
Uso: python generar_notebooks.py

Cada notebook tiene:
  - Badge "Abrir en Colab"
  - Celda de instalación
  - Celdas markdown + código extraídas del .md
"""

import json, re, os, uuid
from pathlib import Path

REPO     = "TomValderrama/manual-introduccion-python-cientifico"
BASE_URL = f"https://colab.research.google.com/github/{REPO}/blob/main/notebooks"
INSTALL  = "!pip install numpy pandas matplotlib scipy windrose plotly --quiet"

CAPITULOS = [
    ("docs/parte1/01_entorno_spyder.md",         "01_fundamentos"),
    ("docs/parte1/01b_spyder_vs_vscode.md",      "01b_entornos"),
    ("docs/parte1/01c_entornos_conda.md",        "01c_conda"),
    ("docs/parte1/02_sintaxis.md",               "02_sintaxis"),
    ("docs/parte1/03_control_flujo.md",          "03_control_flujo"),
    ("docs/parte1/04_funciones_modulos.md",      "04_funciones"),
    ("docs/parte1/04b_debugging.md",             "04b_debugging"),
    ("docs/parte2/05_numpy.md",                  "05_numpy"),
    ("docs/parte2/06_pandas.md",                 "06_pandas"),
    ("docs/parte2/07_lectura_archivos.md",       "07_lectura_archivos"),
    ("docs/parte3/08_matplotlib.md",             "08_matplotlib"),
    ("docs/parte3/09_rosas_polares.md",          "09_rosas_polares"),
    ("docs/parte3/10_figuras_informes.md",       "10_figuras"),
    ("docs/parte3/10b_graficos_interactivos.md", "10b_graficos_interactivos"),
]


def uid():
    return uuid.uuid4().hex[:8]


def md_cell(source):
    lines = source.rstrip().split("\n")
    return {
        "cell_type": "markdown",
        "id": uid(),
        "metadata": {},
        "source": [l + "\n" for l in lines[:-1]] + [lines[-1]],
    }


def code_cell(source):
    lines = source.rstrip().split("\n")
    return {
        "cell_type": "code",
        "id": uid(),
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [l + "\n" for l in lines[:-1]] + [lines[-1]],
    }


def parse_md(path):
    """Devuelve lista de (tipo, contenido): 'md' o 'code'."""
    text = Path(path).read_text(encoding="utf-8")

    # Quitar bloques admonition (!!!)
    text = re.sub(r"!!!.*?\n(?:    .*\n)*", "", text)

    segments = []
    code_re  = re.compile(r"```(\w*)\n(.*?)```", re.DOTALL)
    last     = 0

    for m in code_re.finditer(text):
        before = text[last : m.start()].strip()
        if before:
            segments.append(("md", before))

        lang = m.group(1).lower()
        body = m.group(2).strip()
        if not body:
            last = m.end()
            continue

        if lang in ("python", "py", ""):
            segments.append(("code", body))
        elif lang == "bash":
            # Convertir a celda shell de Colab
            shell = "\n".join("!" + l for l in body.split("\n") if l.strip())
            segments.append(("code", shell))
        # Ignorar otros lenguajes (yaml, json, etc.)

        last = m.end()

    after = text[last:].strip()
    if after:
        segments.append(("md", after))

    return segments


def make_notebook(md_path, nb_name):
    nb_file   = f"notebooks/{nb_name}.ipynb"
    badge_url = f"{BASE_URL}/{nb_name}.ipynb"

    raw   = Path(md_path).read_text(encoding="utf-8")
    title = raw.split("\n")[0].lstrip("# ").strip()

    cells = []

    # Celda 1: título + badge + enlace al manual
    badge = (
        f"# {title}\n\n"
        f"[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)]"
        f"({badge_url})\n\n"
        f"> Capítulo del "
        f"[Manual de Introducción a Python Científico]"
        f"(https://tomvalderrama.github.io/manual-introduccion-python-cientifico/)"
    )
    cells.append(md_cell(badge))

    # Celda 2: instalación
    cells.append(code_cell(INSTALL))

    # Resto del capítulo
    for kind, content in parse_md(md_path):
        if content.strip():
            cells.append(md_cell(content) if kind == "md" else code_cell(content))

    nb = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.10.0"},
            "colab": {"provenance": []},
        },
        "cells": cells,
    }

    with open(nb_file, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    print(f"  {nb_file}  ({len(cells)} celdas)")


if __name__ == "__main__":
    os.makedirs("notebooks", exist_ok=True)
    print(f"Generando {len(CAPITULOS)} notebooks...")
    for md_path, nb_name in CAPITULOS:
        make_notebook(md_path, nb_name)
    print("Listo.")
