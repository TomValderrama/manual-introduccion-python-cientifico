# Pandas

Pandas es la librería principal para manejo de datos tabulares. Su estructura central es el **DataFrame**: una tabla con filas y columnas etiquetadas, similar a una hoja de Excel pero operable desde código.

En el procesamiento de datos oceanográficos, los datos de corrientes, viento y oleaje se manejan como DataFrames de Pandas.

```python
import pandas as pd
```

## Series y DataFrames

Una **Series** es una columna con índice. Un **DataFrame** es una tabla de Series con el mismo índice.

```python
# Series
velocidad = pd.Series([0.08, 0.09, 0.6, 0.07], name='velocidad')

# DataFrame desde diccionario
df = pd.DataFrame({
    'velocidad': [0.08, 0.09, 0.60, 0.07],
    'direccion': [  45,   90,  352,  180],
    'profundidad': [  3,    3,    7,    3],
})
```

## Explorar un DataFrame

```python
df.head()           # primeras 5 filas
df.tail(10)         # últimas 10 filas
df.shape            # (filas, columnas)
df.columns          # nombres de columnas
df.dtypes           # tipo de cada columna
df.describe()       # estadísticas básicas
df.info()           # resumen general: tipos, NaN, memoria
```

## Acceder a datos

```python
# Columna por nombre
df['velocidad']
df[['velocidad', 'direccion']]   # varias columnas
```

### loc vs iloc — etiqueta vs posición

Esta es la distinción que más confunde al principio. La diferencia es simple:

- **`iloc`** — accede por **posición numérica**, como los índices de una lista (0, 1, 2…)
- **`loc`** — accede por **etiqueta del índice**, que puede ser un número, una fecha, un string

```python
# Si el índice del DataFrame es 0, 1, 2... ambos parecen iguales
df.iloc[0]      # primera fila (por posición)
df.loc[0]       # fila con etiqueta 0 (por etiqueta)

# La diferencia importa cuando el índice es una fecha
df = df.set_index('tiempo')   # índice es ahora DatetimeIndex

df.iloc[0]                           # primera fila del DataFrame
df.loc['2025-10-01']                 # fila con esa fecha exacta
df.loc['2025-10-01':'2025-10-31']    # rango de fechas — solo funciona con loc
```

**Regla práctica**: si trabajas con series temporales (índice de fechas), usa `loc`. Si solo necesitas "las primeras N filas" o "la fila en la posición X", usa `iloc`.

```python
# Combinando filas y columnas
df.iloc[0:5, 1:3]                          # filas 0-4, columnas 1-2 (posición)
df.loc['2025-10', ['velocidad', 'dir']]    # octubre, columnas por nombre
```

## Filtrado

```python
# Condición simple
df[df['velocidad'] > 0.5]

# Múltiples condiciones
df[(df['velocidad'] > 0.1) & (df['profundidad'] == 3)]
df[(df['direccion'] < 45) | (df['direccion'] > 315)]

# isin — valores en una lista
df[df['profundidad'].isin([3, 7, 15])]

# notna / isna
df[df['velocidad'].notna()]      # excluir NaN
df[df['velocidad'].isna()]       # solo NaN
```

## Series temporales

En oceanografía, el índice del DataFrame suele ser un `DatetimeIndex`. Esto permite filtrar y agrupar por tiempo de forma muy eficiente.

```python
# Crear índice temporal desde una columna
df['tiempo'] = pd.to_datetime(df['tiempo'])
df = df.set_index('tiempo')

# Filtrar por rango de fechas
df['2025-10':'2026-03']
df.loc['2025-10-01':'2026-03-30']

# Resamplear: promedios horarios, diarios, mensuales
df.resample('1h').mean()    # promedio cada hora
df.resample('1D').max()     # máximo diario
df.resample('1ME').mean()   # promedio mensual
```

### Timezone

Los datos del ADCP y la boya están en UTC. Para convertir a hora local (UTC-3):

```python
from datetime import timezone, timedelta

df.index = df.index.tz_localize('UTC')
df.index = df.index.tz_convert('America/Santiago')
```

## Operaciones por columna

```python
# Crear nuevas columnas
df['vel_nudos'] = df['velocidad'] * 1.944

# Operaciones sobre columnas existentes
df['u'] = df['velocidad'] * np.sin(np.radians(df['direccion']))
df['v'] = df['velocidad'] * np.cos(np.radians(df['direccion']))

# Reemplazar valores
df['velocidad'] = df['velocidad'].replace(-9999, np.nan)

# Aplicar función personalizada
def clasificar_beaufort(vel):
    if vel < 0.3:   return "calma"
    elif vel < 1.5: return "ventolina"
    elif vel < 3.3: return "brisa leve"
    else:           return "brisa moderada o más"

df['beaufort'] = df['velocidad'].apply(clasificar_beaufort)
```

## Estadísticas

```python
df['velocidad'].mean()
df['velocidad'].max()
df['velocidad'].std()
df['velocidad'].quantile(0.95)   # percentil 95

# Por columna
df.mean()
df.describe()

# Contar valores no nulos
df['velocidad'].count()
df['velocidad'].isna().sum()    # cantidad de NaN
```

## groupby — estadísticas por categoría

`groupby` divide el DataFrame en grupos según el valor de una columna, calcula algo dentro de cada grupo, y devuelve los resultados combinados. Es el equivalente en código de "agrupar por X en una tabla pivot de Excel".

```
DataFrame original          Después de groupby('profundidad')
──────────────────          ─────────────────────────────────
profundidad  velocidad       profundidad  velocidad_media
3            0.08            3            0.085
3            0.09            7            0.335
7            0.60            ← promedio dentro de cada grupo
7            0.07
```

```python
# Estadísticas por profundidad
df.groupby('profundidad')['velocidad'].mean()
df.groupby('profundidad')['velocidad'].agg(['mean', 'max', 'std'])

# Estadísticas por mes
df.groupby(df.index.month)['velocidad'].mean()

# Por hora del día (patrón diurno)
df.groupby(df.index.hour)['velocidad'].mean()
```

### Ejemplo real: patrón diurno del viento

```python
patron_diurno = df.groupby(df.index.hour)['velocidad'].mean()
patron_diurno.index.name = 'hora'
```

### groupby con múltiples agregaciones

Cuando se necesita calcular varias estadísticas a la vez, `agg` acepta un diccionario con nombre de salida y función:

```python
resumen = df.groupby('profundidad')['velocidad'].agg(
    media='mean',
    maxima='max',
    p95=lambda x: x.quantile(0.95),
    n_datos='count'
)
```

Esto devuelve un DataFrame con una columna por estadística, nombrada explícitamente — más claro que encadenar varias llamadas separadas.

```python
# Agrupar por dos columnas a la vez
df.groupby(['profundidad', df.index.month])['velocidad'].mean()
# → media por cada combinación (profundidad, mes)
```

## Rolling — ventana deslizante

`rolling` aplica una función sobre una ventana móvil de N filas. Es la forma estándar de suavizar series temporales y calcular estadísticas en un intervalo de tiempo deslizante.

```python
# Suavizado: media móvil de 1 hora (datos cada 10 min → ventana de 6 puntos)
df['vel_suavizada'] = df['velocidad'].rolling(window=6).mean()

# La ventana es centrada por defecto hacia atrás:
# el valor en t es la media de [t-5, t-4, t-3, t-2, t-1, t]
# Las primeras N-1 filas serán NaN porque no hay suficientes datos previos
```

Con series temporales de frecuencia regular, es más claro usar el tamaño de ventana en tiempo:

```python
df['vel_suavizada'] = df['velocidad'].rolling('1h').mean()    # media de 1 hora
df['vel_suavizada'] = df['velocidad'].rolling('6h').mean()    # media de 6 horas
df['std_movil']     = df['velocidad'].rolling('1D').std()     # std diaria móvil
```

```python
# Percentil 95 móvil — más pesado pero válido
df['p95_movil'] = df['velocidad'].rolling('7D').quantile(0.95)
```

!!! tip "Cuándo suavizar"
    Los datos de ADCP tienen ruido acústico y efectos de ondas superficiales. Una media móvil de 10–60 minutos elimina variabilidad de alta frecuencia sin afectar la señal de corriente. No suavizar antes de hacer estadísticas mensuales — eso puede sesgar los resultados.

## pd.cut — crear intervalos

`pd.cut` divide una columna continua en intervalos (bins) y asigna una etiqueta a cada valor. Se usa para construir tablas de incidencia (velocidad × dirección) y estadísticas por rango de profundidad.

```python
# Crear intervalos de velocidad: 0-0.1, 0.1-0.25, 0.25-0.5, 0.5-1.0 m/s
bins   = [0, 0.1, 0.25, 0.5, 1.0]
labels = ['calma', 'leve', 'moderada', 'fuerte']

df['intervalo_vel'] = pd.cut(df['velocidad'], bins=bins, labels=labels)
```

```python
# Número de intervalos iguales — pandas elige los límites automáticamente
df['quintil_vel'] = pd.cut(df['velocidad'], bins=5)

# pd.qcut — misma cantidad de datos en cada intervalo (cuantiles)
df['cuartil_vel'] = pd.qcut(df['velocidad'], q=4, labels=['Q1','Q2','Q3','Q4'])
```

Una vez que cada dato tiene su etiqueta de intervalo, se puede agrupar:

```python
df.groupby('intervalo_vel')['velocidad'].count()   # frecuencia por intervalo
df.groupby('intervalo_vel')['velocidad'].mean()    # media dentro de cada rango
```

## pivot_table — tabla de frecuencias

Las tablas de incidencia (velocidad × dirección) del informe se generan con pivot_table:

```python
# Tabla de frecuencia: velocidad × dirección
tabla = pd.pivot_table(
    df,
    values='velocidad',
    index='intervalo_vel',
    columns='octante',
    aggfunc='count',
    fill_value=0
)

# Normalizar a porcentaje
tabla_pct = tabla / tabla.values.sum() * 100
```

## merge y concat — combinar DataFrames

### concat — apilar filas

```python
# Misma estructura, distintos períodos — apilar verticalmente
df_total = pd.concat([df_septiembre, df_octubre, df_noviembre])

# Si los índices originales se repiten, resetear
df_total = pd.concat([df_sep, df_oct, df_nov], ignore_index=True)

# Para saber de qué DataFrame vino cada fila
df_total = pd.concat(
    [df_sep, df_oct, df_nov],
    keys=['sep', 'oct', 'nov']
)
```

### merge — combinar por columna común

`merge` une dos DataFrames que comparten una columna clave. El parámetro `how` controla qué filas se conservan cuando no hay match:

```python
# inner (default): solo las filas que existen en ambos
df = pd.merge(df_corrientes, df_oleaje, on='tiempo', how='inner')

# left: todas las filas de df_corrientes, NaN donde no hay oleaje
df = pd.merge(df_corrientes, df_oleaje, on='tiempo', how='left')

# outer: todas las filas de ambos, NaN donde falta alguno
df = pd.merge(df_corrientes, df_oleaje, on='tiempo', how='outer')
```

```
df_corrientes    df_oleaje        inner merge       left merge
─────────────    ──────────       ────────────      ──────────
tiempo  vel      tiempo  Hm0      tiempo  vel  Hm0  tiempo  vel  Hm0
10:00   0.3      10:00   1.2      10:00   0.3  1.2  10:00   0.3  1.2
10:10   0.4      10:20   0.8      10:20   0.5  0.8  10:10   0.4  NaN
10:20   0.5                                         10:20   0.5  0.8
```

```python
# Si las columnas clave tienen distinto nombre
df = pd.merge(df_corrientes, df_viento,
              left_on='tiempo_adcp', right_on='tiempo_boya',
              how='left')
```

**Regla práctica**: usar `left` cuando el DataFrame izquierdo es el principal y el derecho agrega información complementaria que puede no estar para todos los instantes. Usar `inner` cuando solo interesan los instantes donde hay datos de ambos instrumentos.

## Manejar NaN

```python
df.dropna()                          # eliminar filas con cualquier NaN
df.dropna(subset=['velocidad'])      # solo si velocidad es NaN
df.fillna(0)                         # rellenar con 0
df['velocidad'].interpolate()        # interpolación lineal
df.ffill()                           # propagar último valor válido hacia adelante
```

## Leer y guardar datos

```python
# Leer
df = pd.read_csv('corrientes.csv', sep=';', parse_dates=['tiempo'])
df = pd.read_excel('corrientes.xlsx', sheet_name='VELOCIDAD')

# Guardar
df.to_csv('resultado.csv', index=False)
df.to_excel('resultado.xlsx', sheet_name='Datos', index=False)
```

!!! tip "Variable Explorer en Spyder"
    Hacer doble clic en un DataFrame en el Variable Explorer de Spyder abre una vista de tabla interactiva donde se pueden ordenar columnas y buscar valores, sin escribir ningún código adicional.
