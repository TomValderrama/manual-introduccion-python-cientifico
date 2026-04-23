# Spyder vs VSCode

Spyder es el mejor punto de partida para análisis de datos: es simple, tiene Variable Explorer y está pensado para trabajar con datos desde el primer día. VSCode es más potente como editor y se adapta mejor cuando el código crece en proyectos multi-archivo.

Este capítulo compara ambos entornos y explica cómo hacer la transición cuando conviene.

## Por qué este manual usa Spyder y no Jupyter

Jupyter es muy popular en ciencia de datos, y es probable que lo encuentres en tutoriales y papers. Sin embargo, para el tipo de trabajo que cubre este manual — pipelines de procesamiento, automatización de informes, análisis reproducibles — Spyder con scripts `.py` tiene ventajas concretas sobre notebooks `.ipynb`.

**El problema de estado de los notebooks**

En Jupyter, las celdas se pueden ejecutar en cualquier orden. Esto crea "estado oculto": variables que existen en memoria de corridas anteriores, resultados que dependen del orden en que ejecutaste las celdas, comportamiento que no se puede reproducir corriendo el notebook de arriba a abajo. En un análisis corto de exploración no importa; en un pipeline de producción es una fuente de errores difíciles de detectar.

```python
# Celda 1
df = pd.read_csv('datos.csv')

# Celda 3 (ejecutada antes que la 2)
df = df[df['velocidad'] > 0]   # modifica df

# Celda 2 (ejecutada después)
print(len(df))   # resultado depende del orden de ejecución
```

En un script `.py` de Spyder el código siempre corre de arriba a abajo. El estado es predecible.

**Los scripts `.py` son importables, los notebooks no**

Cuando el código madura, se organiza en funciones que se reutilizan entre proyectos. Un script `.py` se puede importar directamente:

```python
from utils import calcular_media_vectorial
```

Un notebook `.ipynb` no se puede importar sin conversión previa. Esto hace que el código de un notebook quede "atrapado" en él.

**Git funciona bien con `.py`, mal con `.ipynb`**

Los archivos `.ipynb` incluyen los outputs (gráficos, tablas) dentro del archivo JSON. Un `git diff` de un notebook modificado es ilegible. Con scripts `.py`, los diffs son limpios y el historial de cambios es útil.

**Spyder da lo mismo que Jupyter en lo útil**

Lo que hace atractivo a Jupyter para análisis interactivo — ejecutar código por secciones, ver resultados inmediatamente, inspeccionar variables — también lo tiene Spyder:

| Jupyter | Spyder equivalente |
|---|---|
| Celdas de código | Celdas `# %%` |
| Output inline | Consola IPython |
| Variable inspector | Variable Explorer (más completo) |
| Narrativa en Markdown | Comentarios en el código |

La diferencia es que en Spyder el código vive en un archivo `.py` limpio, no en un JSON con outputs embebidos.

**Cuándo sí usar Jupyter**

Jupyter tiene ventajas reales para comunicar resultados: mezclar texto explicativo, código y gráficos en un documento que otros pueden leer y re-ejecutar. Es el formato estándar para papers reproducibles y tutoriales. Si el objetivo es compartir un análisis con alguien que no va a modificar el código, un notebook bien hecho es ideal. Si el objetivo es construir un pipeline que procese datos y se mantenga en el tiempo, un script `.py` es mejor.

---

## Comparativa directa

| | Spyder | VSCode |
|---|---|---|
| **Variable Explorer** | Integrado, visual, con doble clic en DataFrames | Requiere modo Jupyter interactivo |
| **Celdas `# %%`** | Nativo, `Ctrl+Enter` / `Shift+Enter` | Con extensión Python, funciona igual |
| **Autocompletado** | Básico | Avanzado (Pylance: tipos, docstrings, imports) |
| **Navegación entre archivos** | Limitada | Ir a definición entre módulos, búsqueda global |
| **Git** | No integrado | Diff visual, historial, blame por línea |
| **Terminal** | Consola IPython | Terminal bash/WSL real |
| **Backend Qt5** | Conflicto de event loop | Sin conflicto (Electron ≠ Qt) |
| **Refactoring** | Básico | Renombrar en todo el proyecto, mover código |
| **Curva de aprendizaje** | Baja | Media |
| **Instalación** | Anaconda | Descarga + extensión Python |

## La distinción más importante: pipeline interactivo vs estático

La diferencia real entre Spyder y VSCode no es nivel de experiencia — es el tipo de pipeline:

**Pipeline interactivo**: el procesamiento requiere decisiones humanas en el camino. Cargas los datos, inspeccionas, decides dónde cortar la serie, identificas un offset, limpias anomalías, vuelves a graficar. En este flujo, el Variable Explorer de Spyder no es una rueda de entrenamiento — es una herramienta de trabajo. Ver el DataFrame en tiempo real, hacer doble clic para abrirlo como tabla, comparar shapes antes y después de un filtro: todo eso acelera el trabajo de procesamiento interactivo.

**Pipeline estático**: el código corre de principio a fin sin intervención. Leer archivos, procesar, generar figuras, exportar resultados. Aquí Spyder no agrega valor — un script ejecutado desde la terminal de VSCode hace exactamente lo mismo con mejor soporte de proyecto y Git.

## Cuándo quedarse en Spyder

- El procesamiento requiere inspeccionar y tomar decisiones sobre los datos (offset, recortes, limpieza manual)
- Usas el Variable Explorer activamente para ver el estado intermedio de arrays y DataFrames
- El flujo es exploratorio: cargar, graficar, ajustar, volver a graficar
- Trabajas con un dataset por vez y el script cabe en un archivo

## Cuándo usar VSCode

- El pipeline corre completo sin intervención (genera figuras, exporta, automatiza)
- El proyecto tiene varios módulos que se importan entre sí
- Usas Git activamente y quieres diffs sin salir del editor
- Desarrollas herramientas con interfaz (matplotlib interactivo, Qt5) sin conflictos de event loop
- Necesitas conectarte a un servidor remoto (extensión Remote-SSH)
- El código ya está maduro y entra en fase de mantenimiento

## Configurar VSCode para análisis de datos

### Instalación mínima

1. Descargar VSCode: [code.visualstudio.com](https://code.visualstudio.com)
2. Instalar extensiones:
   - **Python** (Microsoft) — soporte base
   - **Pylance** — autocompletado avanzado con inferencia de tipos

### Seleccionar el intérprete de Python

`Ctrl+Shift+P` → "Python: Select Interpreter" → elegir el Python de Anaconda (`conda base` o el entorno que uses).

### Celdas `# %%` en VSCode

Las celdas funcionan exactamente igual que en Spyder. Con la extensión Python instalada:

```python
# %% Cargar datos
import pandas as pd
df = pd.read_csv('corrientes.csv')

# %% Graficar
import matplotlib.pyplot as plt
plt.plot(df['velocidad'])
plt.show()
```

- `Shift+Enter` ejecuta la celda y avanza
- `Ctrl+Enter` ejecuta la celda sin avanzar
- Se abre un panel "Jupyter Interactive" donde aparecen los outputs

### Variable Explorer equivalente

El panel Jupyter Interactive muestra las variables activas. También se puede:

```python
# En la celda, inspeccionar directamente
df.head()        # muestra las primeras filas como tabla
df.dtypes        # tipos de columnas
df.describe()    # estadísticas
```

Para abrir un DataFrame como tabla visual: instalar la extensión **Data Wrangler** (Microsoft).

### Configurar el backend de matplotlib

En VSCode, el backend inline se activa automáticamente en el modo interactivo. Para ventanas separadas:

```python
%matplotlib tk    # Tkinter — funciona bien
%matplotlib qt5   # Qt5 — también funciona bien (sin conflicto con VSCode)
```

### Atajos equivalentes a Spyder

**Ejecución y edición**

| Acción | Spyder | VSCode |
|---|---|---|
| Ejecutar celda | `Ctrl+Enter` | `Shift+Enter` |
| Ejecutar celda y avanzar | `Shift+Enter` | `Shift+Enter` |
| Ejecutar selección | `F9` | `Shift+Enter` (con selección) |
| Comentar / descomentar | `Ctrl+1` | `Ctrl+/` |

**Navegación y búsqueda**

| Acción | Spyder | VSCode |
|---|---|---|
| Ir a definición | `Ctrl+G` | `F12` |
| Buscar en archivo | `Ctrl+F` | `Ctrl+F` |
| Buscar en todo el proyecto | — | `Ctrl+Shift+F` |
| Paleta de comandos | — | `Ctrl+Shift+P` |

### Terminal integrado

`Ctrl+ñ` (o `Ctrl+\``) abre una terminal bash/WSL real dentro de VSCode. Útil para correr scripts completos, git, o herramientas de línea de comandos:

```bash
python generar_informe.py
bash publicar.sh
git log --oneline -10
```

## Jupyter en VSCode

VSCode soporta notebooks `.ipynb` nativamente. Para abrir o crear uno: `Ctrl+Shift+P` → "Create new Jupyter Notebook".

La ventaja sobre JupyterLab clásico: el editor de VSCode (autocompletado, Pylance) funciona dentro de las celdas del notebook.

## Flujo mixto recomendado

No es necesario elegir uno y abandonar el otro. La combinación más práctica:

1. **Procesamiento interactivo en Spyder**: inspeccionar datos, identificar problemas, tomar decisiones (offset, recortes, limpieza). El Variable Explorer hace este trabajo más rápido.
2. **Pipeline automático en VSCode + terminal**: cuando el procesamiento ya está definido y corre sin intervención. Ejecutar desde terminal, gestionar Git, mantener el proyecto multi-archivo.
3. **Git en VSCode**: commits, diffs visuales, historial — independientemente de dónde se escribió el código.

El código funciona igual en ambos entornos. Lo que cambia es qué tan cómodo es cada flujo de trabajo según la etapa del proyecto.

### Cuándo salir del IDE y correr desde terminal

Hay casos en que Spyder y VSCode se interponen en vez de ayudar:

- **Script con menú de procesamiento** (`input()` en un loop): Spyder ejecuta en un kernel IPython que no maneja bien la entrada interactiva en modo batch.
- **GUI propia con matplotlib o Tkinter**: el IDE ya tiene un event loop corriendo; abrir otro genera conflictos. TkAgg suele funcionar en Spyder con `%matplotlib tk`, pero Qt5Agg frecuentemente no.
- **Combinación de ambos** (menú + ventana gráfica): ningún backend funciona de forma confiable dentro del IDE.

En esos casos la solución es correr el script directamente desde una terminal:

```bash
# PowerShell o cmd (usa el Python de Windows, TkAgg nativo)
python mi_script.py

# Terminal WSL (requiere WSLg en Windows 11, o un servidor X en Windows 10)
python mi_script.py
```

El script toma control del proceso completo: puede pedir input, abrir ventanas y cerrarlas sin conflicto con el IDE. Ver cap. 10b para el patrón `plt.ion()` + `plt.pause()` que permite combinar un menú de texto con figuras interactivas.
