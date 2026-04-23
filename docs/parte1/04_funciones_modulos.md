# Funciones y módulos

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/TomValderrama/manual-introduccion-python-cientifico/blob/main/notebooks/04_funciones.ipynb)


## Funciones

### ¿Por qué hacer una función?

Cuando un mismo bloque de código aparece más de una vez — aunque sea con pequeñas variaciones — conviene convertirlo en función. Así se escribe una sola vez, se prueba una sola vez, y si hay que corregirlo se cambia en un solo lugar.

```python
# Sin función: repetir la misma lógica para cada mes
vel_oct = datos_oct['velocidad']
media_oct = vel_oct.mean()
std_oct   = vel_oct.std()
max_oct   = vel_oct.max()
print(f"Oct — media={media_oct:.2f}  std={std_oct:.2f}  max={max_oct:.2f}")

vel_nov = datos_nov['velocidad']
media_nov = vel_nov.mean()
std_nov   = vel_nov.std()
max_nov   = vel_nov.max()
print(f"Nov — media={media_nov:.2f}  std={std_nov:.2f}  max={max_nov:.2f}")

# Con función: escribir la lógica una vez
def reportar_estadisticas(df, nombre):
    vel = df['velocidad']
    print(f"{nombre} — media={vel.mean():.2f}  std={vel.std():.2f}  max={vel.max():.2f}")

reportar_estadisticas(datos_oct, 'Oct')
reportar_estadisticas(datos_nov, 'Nov')
reportar_estadisticas(datos_dic, 'Dic')
```

La función no solo ahorra líneas — hace el código más fácil de entender porque el nombre `reportar_estadisticas` describe exactamente qué hace.

Una función agrupa código reutilizable bajo un nombre. En un pipeline de procesamiento de datos casi toda la lógica está organizada en funciones: una para leer datos, otra para filtrar, otra para graficar, etc.

```python
def calcular_media_vectorial(velocidades, direcciones):
    """Calcula la dirección y velocidad resultante del vector medio."""
    import numpy as np
    u = velocidades * np.sin(np.radians(direcciones))
    v = velocidades * np.cos(np.radians(direcciones))
    u_media = np.mean(u)
    v_media = np.mean(v)
    vel_media = np.sqrt(u_media**2 + v_media**2)
    dir_media = np.degrees(np.arctan2(u_media, v_media)) % 360
    return vel_media, dir_media
```

### Sintaxis básica

```python
def nombre_funcion(parametro1, parametro2):
    # cuerpo de la función
    resultado = parametro1 + parametro2
    return resultado

# Llamar la función
total = nombre_funcion(3, 5)   # total = 8
```

### Parámetros por defecto

```python
def leer_corrientes(ruta, sep=';', skiprows=0, encoding='utf-8'):
    import pandas as pd
    return pd.read_csv(ruta, sep=sep, skiprows=skiprows, encoding=encoding)

# Uso mínimo (usa los valores por defecto)
df = leer_corrientes('datos.csv')

# Sobreescribir un parámetro específico
df = leer_corrientes('datos.csv', sep=',', skiprows=2)
```

### Múltiples valores de retorno

Python puede retornar múltiples valores como una tupla:

```python
def estadisticas(datos):
    import numpy as np
    return np.mean(datos), np.max(datos), np.std(datos)

media, maximo, desviacion = estadisticas(velocidades)
```

### Argumentos con nombre (kwargs)

```python
def guardar_figura(fig, nombre, dpi=150, formato='png'):
    ruta = f"figuras/{nombre}.{formato}"
    fig.savefig(ruta, dpi=dpi, bbox_inches='tight')
    print(f"Figura guardada: {ruta}")

# Se pueden pasar en cualquier orden si se nombran
guardar_figura(fig, "rosa_corrientes", formato='pdf', dpi=300)
```

## Módulos e imports

Un módulo es un archivo `.py` que contiene funciones, clases y variables. Las librerías como NumPy, Pandas y Matplotlib son colecciones de módulos.

### Formas de importar

```python
# Importar la librería completa
import numpy

# Con alias (convención estándar)
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Importar solo lo que se necesita
from datetime import datetime, timezone
from pathlib import Path
```

### Importar funciones propias

Si tienes tus funciones en otro archivo, por ejemplo `utils.py`:

```python
# utils.py
def convertir_uv(velocidad, direccion):
    import numpy as np
    u = velocidad * np.sin(np.radians(direccion))
    v = velocidad * np.cos(np.radians(direccion))
    return u, v
```

Se importa así desde otro script:

```python
from utils import convertir_uv

u, v = convertir_uv(0.35, 45)
```

### sys.path — importar desde otra carpeta

Cuando el archivo que necesitas está en otro directorio, hay que agregar esa ruta al path de Python:

```python
import sys
sys.path.insert(0, '/ruta/a/mi/libreria')

from mi_modulo import mi_funcion
```

Esto se usa constantemente en el pipeline de procesamiento, por ejemplo en `run_pipeline.py` para cargar los módulos de cada instrumento.

### importlib — carga dinámica

Cuando la ruta del módulo se conoce solo en tiempo de ejecución (por ejemplo, depende de qué proyecto se está procesando), se usa `importlib`:

```python
import importlib.util

def cargar_modulo(ruta_archivo):
    spec = importlib.util.spec_from_file_location("modulo", ruta_archivo)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo

# Cargar el script de notas del analista
notas = cargar_modulo('/proyectos/LosVilos/notas_informe.py')
parrafo_viento = notas.parrafo_viento
```

## Organizar código en módulos

A medida que los scripts crecen, conviene separar el código en archivos temáticos. Un ejemplo de estructura para un proyecto de análisis oceanográfico:

```
ocean_data_analysis/
├── __init__.py
├── read_data.py          ← funciones de lectura
├── preprocessing.py      ← filtros y correcciones
├── wave_processing.py    ← análisis de oleaje
├── wind_figures.py       ← figuras de viento
├── current_z_figures.py  ← figuras de corrientes
└── extreme_events.py     ← análisis de eventos extremos
```

El archivo `__init__.py` (puede estar vacío) le indica a Python que esa carpeta es un paquete importable.

## Scope (alcance de variables)

Las variables definidas dentro de una función son locales — no existen fuera de ella:

```python
def procesar():
    resultado = 42      # variable local
    return resultado

procesar()
print(resultado)        # NameError: resultado no existe aquí
```

Para compartir datos entre funciones, lo correcto es usar el valor de retorno, no variables globales.

!!! tip "Buena práctica"
    Escribe funciones pequeñas que hagan una sola cosa. Es más fácil probarlas, reutilizarlas y entenderlas. Si una función supera las 50 líneas, probablemente conviene dividirla.
