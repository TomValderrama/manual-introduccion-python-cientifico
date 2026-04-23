# NumPy

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/TomValderrama/manual-introduccion-python-cientifico/blob/main/notebooks/05_numpy.ipynb)


NumPy es la librería fundamental para cálculo numérico en Python. Su estructura central es el **array**: un arreglo multidimensional de valores del mismo tipo, mucho más eficiente que una lista de Python para operaciones matemáticas.

```python
import numpy as np
```

## Arrays vs listas de Python

La pregunta más común al empezar con NumPy es: ¿cuándo usar un array y cuándo una lista?

| | Lista de Python | Array de NumPy |
|---|---|---|
| Tipos de elementos | Mixtos (`[1, "texto", True]`) | Todos del mismo tipo |
| Operaciones matemáticas | Requieren un loop | Directas sobre todo el array |
| Velocidad | Lenta para cálculos | 10-100× más rápida |
| Uso típico | Colecciones generales, texto | Series numéricas, matrices |

```python
# Lista — la operación no funciona como se espera
velocidades_lista = [0.08, 0.09, 0.6, 0.07]
velocidades_lista * 1.944    # repite la lista, no multiplica cada elemento

# Array — la operación se aplica a cada elemento
velocidades = np.array([0.08, 0.09, 0.6, 0.07])
velocidades * 1.944          # [0.156, 0.175, 1.166, 0.136] — correcto
```

**Regla práctica**: si vas a hacer cálculos (sumas, medias, trigonometría), usa arrays. Si solo necesitas guardar una colección de cosas para iterar sobre ellas, una lista está bien.

## Arrays

```python
# Desde una lista
velocidades = np.array([0.08, 0.09, 0.6, 0.07, 0.08, 0.09, 0.10])

# Array de ceros o unos
np.zeros(12)           # [0. 0. 0. ... 0.]
np.ones((3, 4))        # matriz 3×4 de unos

# Secuencias
np.arange(0, 24, 2)    # [0, 2, 4, ..., 22]
np.linspace(0, 1, 50)  # 50 puntos equiespaciados entre 0 y 1
```

### dtype — el tipo de los elementos

Cada array tiene un `dtype` que determina qué tipo de número almacena y cuántos bits usa:

```python
vel = np.array([0.08, 0.09, 0.6, 0.07])
vel.dtype    # float64 — el default para números decimales
```

| dtype | Bits | Precisión | Uso típico |
|---|---|---|---|
| `float64` | 64 | ~15 dígitos | Default de NumPy, máxima precisión |
| `float32` | 32 | ~7 dígitos | Archivos NetCDF, ahorra memoria |
| `int32` | 32 | enteros ±2.1×10⁹ | Índices, contadores |
| `int64` | 64 | enteros grandes | Timestamps en nanosegundos |
| `uint8` | 8 | enteros 0–255 | Imágenes (píxeles) |

**Por qué importa**: los archivos NetCDF y muchos instrumentos oceanográficos almacenan datos en `float32` para ahorrar espacio. Cuando los lees con xarray o NumPy, los datos ya vienen como `float32`. Si mezclas `float32` con `float64` en una operación, NumPy promueve todo a `float64` — lo cual está bien, pero puede sorprender.

```python
# Verificar
vel.dtype                 # float64

# Especificar al crear
vel32 = np.array([0.08, 0.09, 0.6], dtype=np.float32)
vel32.dtype               # float32

# Convertir
vel32 = vel.astype(np.float32)   # float64 → float32
vel64 = vel32.astype(np.float64) # float32 → float64
```

```python
# Leer desde NetCDF (xarray) — frecuentemente viene como float32
import xarray as xr
ds = xr.open_dataset('corrientes.nc')
ds['velocidad'].dtype    # float32

# Convertir si necesitas precisión para análisis espectral
vel64 = ds['velocidad'].values.astype(np.float64)
```

!!! warning "float32 en análisis espectral"
    La pérdida de precisión de float32 (~7 dígitos) rara vez importa en estadísticas descriptivas. Sí puede importar en análisis espectral o cuando se hacen muchas operaciones encadenadas sobre los mismos datos. En esos casos conviene convertir a float64 antes de calcular.

### Arrays 2D — matrices

En corrientes se trabaja frecuentemente con matrices de `(tiempo × profundidad)`:

```python
# Matriz de velocidades: 5 ensembles × 11 profundidades
datos = np.array([
    [0.08, 0.09, 0.6,  0.07, 0.08, 0.09, 0.10, 0.09, 0.08, 0.07, 0.06],
    [0.07, 0.08, 0.55, 0.06, 0.07, 0.08, 0.09, 0.08, 0.07, 0.06, 0.05],
    # ...
])

datos.shape    # (5, 11) — filas × columnas
datos.ndim     # 2
datos.size     # 55 — total de elementos
```

## Operaciones vectorizadas y broadcasting

La ventaja de NumPy es que las operaciones se aplican a todo el array sin necesidad de un loop. A esto se le llama **vectorización**:

```python
vel = np.array([0.08, 0.09, 0.6, 0.07])

# Operaciones elemento a elemento
vel * 1.944        # convertir m/s a nudos
vel ** 2           # cuadrado de cada elemento
np.sqrt(vel)       # raíz cuadrada
np.log(vel)        # logaritmo natural

# Comparación — devuelve array de booleanos
vel > 0.5          # [False, False, True, False]
```

**Broadcasting** es la regla que permite operar un array con un escalar (o con arrays de distinta forma compatible). NumPy "expande" el escalar para que coincida con el tamaño del array:

```python
vel = np.array([0.08, 0.09, 0.6, 0.07])

# En vez de hacer un loop para convertir cada elemento:
# for i in range(len(vel)):
#     vel[i] = vel[i] * 1.944

# NumPy lo hace solo — aplica el *1.944 a cada elemento:
vel * 1.944    # [0.156, 0.175, 1.166, 0.136]

# Sumar dos arrays del mismo tamaño — suma elemento a elemento:
u = np.array([0.1, 0.2, 0.3])
v = np.array([0.4, 0.5, 0.6])
magnitud = np.sqrt(u**2 + v**2)   # calcula raíz de (u²+v²) para cada par
```

### Conversión velocidad/dirección ↔ componentes U, V

Esta operación es fundamental en oceanografía y aparece en múltiples scripts del pipeline:

```python
def uv_desde_vel_dir(velocidad, direccion_grad):
    """Convierte (velocidad, dirección) a componentes (U, V)."""
    dir_rad = np.radians(direccion_grad)
    u = velocidad * np.sin(dir_rad)   # componente Este
    v = velocidad * np.cos(dir_rad)   # componente Norte
    return u, v

def vel_dir_desde_uv(u, v):
    """Convierte (U, V) a (velocidad, dirección)."""
    velocidad  = np.sqrt(u**2 + v**2)
    direccion  = np.degrees(np.arctan2(u, v)) % 360
    return velocidad, direccion
```

## Indexación y slicing

```python
prof = np.array([3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23])

prof[0]        # 3  — primer elemento
prof[-1]       # 23 — último
prof[2:5]      # [7, 9, 11]
prof[::2]      # [3, 7, 11, 15, 19, 23] — cada dos

# En 2D: [fila, columna]
datos[0, :]    # primera fila completa (ensemble 0, todas las profundidades)
datos[:, 2]    # columna 2 completa (todos los ensembles, profundidad 7 m)
datos[1:3, 3:6]  # submatriz
```

### Indexación booleana — filtrado

```python
vel = np.array([0.08, 0.09, 0.6, 0.07, 0.55, 0.09])

# Seleccionar solo los valores > 0.5
vel[vel > 0.5]         # [0.6, 0.55]

# Reemplazar valores fuera de rango con NaN
vel[vel > 0.5] = np.nan
```

## Estadísticas

```python
vel = np.array([0.08, 0.09, 0.60, 0.07, 0.08])

np.mean(vel)        # media
np.median(vel)      # mediana
np.std(vel)         # desviación estándar
np.max(vel)         # máximo
np.min(vel)         # mínimo
np.percentile(vel, 95)  # percentil 95

np.argmax(vel)      # índice del máximo → 2
```

### Funciones que ignoran NaN

Cuando los datos tienen valores faltantes (`NaN`), usar las versiones `nan*`:

```python
np.nanmean(vel)
np.nanmax(vel)
np.nanstd(vel)
np.nanpercentile(vel, 95)
```

### Estadísticas por eje en matrices

```python
datos.mean(axis=0)   # media por profundidad (a lo largo del tiempo)
datos.mean(axis=1)   # media por ensemble (a lo largo de profundidades)
datos.max(axis=0)    # máximo por profundidad
```

## Funciones trigonométricas

NumPy trabaja en radianes. Para datos de dirección oceánica (en grados):

```python
np.radians(180)      # π
np.degrees(np.pi)    # 180.0

np.sin(np.radians(90))   # 1.0
np.cos(np.radians(0))    # 1.0

# arctan2 — dirección del vector (U, V)
u, v = 0.5, 0.5
direccion = np.degrees(np.arctan2(u, v)) % 360   # 45.0°
```

## NaN — valores faltantes

```python
np.nan                      # valor especial "Not a Number"
np.isnan(vel)               # array booleano: True donde hay NaN
np.isnan(vel).sum()         # cantidad de NaN
~np.isnan(vel)              # máscara de datos válidos

# Contar datos válidos
datos_validos = vel[~np.isnan(vel)]
```

## Operaciones útiles

```python
# Diferencia entre elementos consecutivos
np.diff(np.array([1, 3, 6, 10]))   # [2, 3, 4]

# Concatenar arrays
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
np.concatenate([a, b])             # [1, 2, 3, 4, 5, 6]

# Apilar matrices verticalmente
np.vstack([datos[:2, :], datos[3:, :]])

# Ordenar
np.sort(vel)                       # copia ordenada
vel.argsort()                      # índices que ordenarían el array

# Redondear
np.round(3.14159, 2)               # 3.14
```

!!! tip "NumPy vs listas de Python"
    Para operaciones matemáticas sobre grandes conjuntos de datos, NumPy es entre 10 y 100 veces más rápido que un loop sobre una lista Python. En series temporales de 6 meses con datos cada 10 minutos (~26.000 registros), esa diferencia es significativa.
