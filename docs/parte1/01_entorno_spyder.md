# Entorno de desarrollo

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/TomValderrama/manual-introduccion-python-cientifico/blob/main/notebooks/01_fundamentos.ipynb)


Python se puede escribir y ejecutar desde varios entornos. Cada uno tiene un perfil distinto — la elección depende del tipo de tarea y del momento del proyecto.

## Comparativa de entornos

| Entorno | Mejor para | Instalación |
|---|---|---|
| **Spyder** | Análisis interactivo, explorar datos, perfil científico | Anaconda |
| **VSCode** | Proyectos multi-archivo, Git, scripts de producción | Descarga directa |
| **JupyterLab** | Reportes con código + texto, compartir resultados | `pip install jupyterlab` |
| **Google Colab** | Sin instalación, acceso a GPU, colaboración | Solo navegador |

Este capítulo se enfoca en **Spyder**, que es el más adecuado para empezar: tiene Variable Explorer integrado, permite ejecutar código por secciones y está diseñado específicamente para análisis de datos. Las secciones al final del capítulo describen cuándo conviene cambiar a VSCode o Jupyter.

## Spyder

Spyder es el entorno de desarrollo recomendado para análisis científico en Python. A diferencia de otros editores, está diseñado específicamente para trabajar con datos: tiene un explorador de variables integrado, una consola interactiva y permite ejecutar código por secciones.

## Instalación

La forma más sencilla es instalar **Anaconda**, que incluye Python, Spyder y las librerías científicas principales:

[https://www.anaconda.com/download](https://www.anaconda.com/download)

## La interfaz de Spyder

Spyder tiene tres paneles principales:

```
┌─────────────────────┬──────────────────────┐
│                     │  Variable Explorer   │
│      Editor         │  (variables activas) │
│    (tu código)      ├──────────────────────┤
│                     │  Consola IPython     │
│                     │  (resultados)        │
└─────────────────────┴──────────────────────┘
```

- **Editor**: donde escribes y guardas tu script `.py`
- **Consola IPython**: donde se ejecuta el código y se muestran resultados
- **Variable Explorer**: muestra todas las variables activas, sus tipos y valores — muy útil para inspeccionar DataFrames y arrays

## Ejecutar código

| Acción | Atajo |
|--------|-------|
| Ejecutar el script completo | `F5` |
| Ejecutar la línea actual | `F9` |
| Ejecutar una selección | Seleccionar + `F9` |
| Ejecutar una celda | `Ctrl + Enter` |
| Ejecutar celda y avanzar | `Shift + Enter` |

## Atajos de edición esenciales

| Acción | Atajo |
|--------|-------|
| Comentar / descomentar selección | `Ctrl + 1` |
| Insertar separador de celda `# %%` | `Ctrl + 2` |
| Duplicar línea | `Ctrl + D` |
| Mover línea arriba / abajo | `Alt + ↑ / ↓` |
| Buscar en el archivo | `Ctrl + F` |
| Ir a definición de función | `Ctrl + G` |

`Ctrl + 1` es especialmente útil para desactivar temporalmente un bloque de código sin borrarlo. `Ctrl + 2` inserta un `# %%` en la posición del cursor, creando una nueva celda ejecutable en ese punto.

## Celdas de código

Las celdas permiten dividir el script en bloques ejecutables de forma independiente, similar a un notebook pero dentro de un archivo `.py` normal.

Se definen con `# %%`:

```python
# %% Cargar datos
import pandas as pd
df = pd.read_csv('corrientes.csv')

# %% Graficar
import matplotlib.pyplot as plt
plt.plot(df['velocidad'])
plt.show()
```

Cada bloque `# %%` se puede ejecutar por separado con `Ctrl + Enter`. Esto es muy útil para procesar datos paso a paso sin reejecutar todo el script.

## Variable Explorer

El explorador de variables muestra en tiempo real:

- Nombre y tipo de cada variable
- Dimensiones de arrays y DataFrames
- Vista previa de los valores

Se puede hacer doble clic en un DataFrame para abrirlo en una tabla interactiva, o en un array para ver su contenido completo.

## Consola IPython

La consola acepta comandos directos sin necesidad de estar en el editor:

```python
# Ver las primeras filas de un DataFrame
df.head()

# Ver el tipo de una variable
type(df)

# Obtener ayuda de una función
help(pd.read_csv)
# o más rápido:
pd.read_csv?
```

## Configuración recomendada

Algunas opciones útiles en **Tools → Preferences**:

- **Editor → mostrar números de línea**: facilita depuración
- **IPython console → Graphics → Backend: Inline**: los gráficos aparecen en la consola (recomendado para análisis)
- **IPython console → Graphics → Backend: Tkinter**: cada gráfico abre en ventana separada, liviana e interactiva (zoom, pan, guardar)
- **IPython console → Graphics → Backend: Qt5**: similar a Tkinter pero más pesado; en algunos equipos es lento o inestable

También se puede cambiar el backend por sesión desde la consola sin tocar las preferencias:

```python
%matplotlib inline   # figuras en consola
%matplotlib tk       # ventana Tkinter interactiva
%matplotlib qt5      # ventana Qt5
```

### Cuándo usar cada backend

| Situación | Backend |
|---|---|
| Explorar datos, iterar rápido | Inline |
| Revisar figura con zoom o hacer clics sobre ella | Tkinter |
| Script automático que solo guarda PNG | `matplotlib.use('Agg')` antes de importar pyplot |

### Tkinter vs Qt5 — por qué Tkinter es más estable en Spyder

Spyder está construido sobre Qt5 (PyQt5). Cuando se usa el backend Qt5Agg, matplotlib intenta crear ventanas Qt5 dentro del mismo event loop que ya está usando Spyder — pueden producirse conflictos, ventanas lentas o cierres inesperados.

Tkinter tiene su propio event loop completamente independiente de Qt, por eso no interfiere con Spyder.

En **VSCode** este problema no existe: VSCode está hecho en Electron (Chromium), no en Qt. El backend Qt5Agg abre ventanas Qt5 de forma independiente y funciona sin conflictos.

Otra causa de ventanas que "se congelan": si el script hace procesamiento pesado (imágenes, OCR, cálculos largos) en el mismo hilo que la ventana gráfica, el event loop no puede responder a clics mientras Python está ocupado. Esto ocurre con cualquier backend, pero Qt5 lo manifiesta más visiblemente.

| | Tkinter | Qt5 |
|---|---|---|
| Integración con Spyder | Sin conflictos | Puede interferir con el event loop |
| Integración con VSCode | Bien | Bien |
| Peso | Liviano, incluido en Python | Pesado, requiere PyQt5/PySide2 |
| Widgets interactivos | Básicos (zoom, pan, guardar) | Avanzados (sliders, botones personalizados) |
| Uso recomendado | Backend interactivo general | Herramientas con interfaz propia |

!!! tip "Recomendación"
    Usar **Inline** como predeterminado en Spyder. Cambiar a **Tkinter** cuando se necesita interactividad. Qt5 solo tiene ventaja real si se construye una interfaz con botones o controles propios, y en ese caso es mejor trabajar en VSCode o en un script independiente fuera de Spyder.

## VSCode

Visual Studio Code es un editor de propósito general con soporte de primera clase para Python. No está diseñado específicamente para análisis de datos, pero tiene ventajas claras cuando el proyecto crece.

**Instalar**: [code.visualstudio.com](https://code.visualstudio.com). Luego instalar la extensión **Python** (Microsoft) y opcionalmente **Pylance** para autocompletado avanzado.

### Ventajas sobre Spyder

- **Editor más potente**: autocompletado inteligente entre archivos, ir a definición entre módulos, refactoring, buscar y reemplazar en todo el proyecto
- **Git integrado**: diff visual, historial de commits, blame por línea, sin salir del editor
- **Terminal real**: bash/WSL integrado directamente, útil para correr scripts, git, pandoc
- **Multi-archivo**: navegación entre archivos de un paquete Python es mucho más fluida
- **Sin conflicto Qt5**: VSCode usa Electron (no Qt), por lo que el backend Qt5Agg de matplotlib funciona sin interferencias
- **Extensiones**: SSH remoto (trabajar en servidores Linux), Jupyter, Docker, soporte para otros lenguajes en el mismo proyecto

### Cuándo conviene migrar a VSCode

- El proyecto tiene varios archivos `.py` que se importan entre sí
- Se trabaja con Git activamente
- Se desarrolla una herramienta con interfaz interactiva (matplotlib + clicks, sliders)
- Se necesita conectarse a un servidor remoto (cluster para CROCO, por ejemplo)

### Variable Explorer en VSCode

VSCode no tiene un Variable Explorer tan completo como Spyder. La alternativa es usar el modo **Jupyter** (celdas `# %%` con el kernel interactivo), que muestra variables y permite inspeccionarlas. Para DataFrames, `df.head()` o `df.describe()` en la terminal interactiva cumplen el mismo rol.

## JupyterLab y Jupyter Notebook

Jupyter permite mezclar código Python, texto explicativo (Markdown) y resultados (gráficos, tablas) en un mismo documento interactivo llamado **notebook** (`.ipynb`).

```bash
pip install jupyterlab
jupyter lab   # abre en el navegador
```

### Cuándo usar Jupyter

- **Exploración inicial de datos nuevos**: ver los datos, graficar, entender la estructura
- **Reportes reproducibles**: compartir análisis donde el lector puede ver el código y los resultados juntos
- **Tutoriales y documentación**: la mayoría de tutoriales de xarray, pandas, geopandas están en notebooks
- **Colaboración**: Google Colab permite compartir y ejecutar notebooks sin instalar nada

### Limitaciones de Jupyter para producción

Los notebooks tienen desventajas cuando el código madura:

- El orden de ejecución de celdas puede ser arbitrario — un notebook con celdas ejecutadas fuera de orden produce resultados incorrectos sin avisar
- Difíciles de versionar con Git (el formato `.ipynb` incluye outputs, lo que genera diffs enormes)
- No se pueden importar como módulos desde otros scripts
- La refactorización y navegación entre archivos es más limitada

**Regla práctica**: usar Jupyter para explorar y comunicar resultados; convertir el código útil a scripts `.py` para producción.

## PyCharm

PyCharm (JetBrains) es un IDE profesional orientado al desarrollo de software en Python. Tiene herramientas avanzadas de refactoring, depuración y gestión de proyectos que lo hacen muy popular en desarrollo de aplicaciones y backend.

Para análisis de datos y scripting científico no es la primera opción: no tiene Variable Explorer, su curva de aprendizaje es mayor, y la versión completa es de pago (existe una Community Edition gratuita). Se menciona aquí porque es frecuente encontrarlo en tutoriales y comparativas, pero no se cubre en este manual — para el tipo de trabajo que se describe, Spyder y VSCode cubren mejor el espectro.

## Google Colab

Jupyter en la nube de Google. No requiere instalar nada — solo un navegador y cuenta de Google.

- URL: [colab.research.google.com](https://colab.research.google.com)
- Acceso gratuito a GPU (útil para modelos de deep learning o procesamiento de imágenes pesado)
- Se integra con Google Drive para leer y guardar archivos
- Ideal para compartir análisis con alguien que no tiene Python instalado

La limitación principal: la sesión se desconecta después de un tiempo de inactividad y los datos temporales se pierden. Para trabajo continuo es mejor un entorno local.
