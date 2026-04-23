# Figuras para informes

En un pipeline de informes automatizados las figuras no solo se visualizan en Spyder, sino que se guardan como archivos PNG para luego insertarlas en el informe Word. Esto implica cuidar resolución, tamaño, fuente y nomenclatura de archivos.

## Estilo consistente

Definir un estilo base al comienzo del script garantiza que todas las figuras tengan el mismo aspecto:

```python
import matplotlib.pyplot as plt
import matplotlib as mpl

# Estilo global
mpl.rcParams.update({
    'font.family':      'sans-serif',
    'font.size':        10,
    'axes.titlesize':   11,
    'axes.labelsize':   10,
    'xtick.labelsize':  9,
    'ytick.labelsize':  9,
    'legend.fontsize':  9,
    'figure.dpi':       100,
    'axes.grid':        True,
    'grid.alpha':       0.3,
    'axes.spines.top':  False,
    'axes.spines.right':False,
})
```

O usar un estilo predefinido:

```python
plt.style.use('seaborn-v0_8-whitegrid')
```

## Guardar con calidad para informe

```python
fig.savefig(
    ruta_figura,
    dpi=150,               # 150 dpi es suficiente para Word
    bbox_inches='tight',   # elimina márgenes en blanco
    facecolor='white'      # fondo blanco (no transparente)
)
plt.close(fig)
```

## Nomenclatura de archivos de figura

El autoinforme busca las figuras por nombre. Es importante seguir una convención estricta:

```python
import os

carpeta_figuras = os.path.join(ruta_proyecto, 'figuras_magnitud')
os.makedirs(carpeta_figuras, exist_ok=True)

# Nomenclatura usada en el pipeline de corrientes
fig_serie.savefig(    os.path.join(carpeta_figuras, 'serie_velocidad.png'),    dpi=150, bbox_inches='tight')
fig_rosa.savefig(     os.path.join(carpeta_figuras, 'rosa_corrientes_3m.png'), dpi=150, bbox_inches='tight')
fig_heatmap.savefig(  os.path.join(carpeta_figuras, 'heatmap_velocidad.png'),  dpi=150, bbox_inches='tight')
```

## Figuras por profundidad

Cuando se genera una figura por cada profundidad (rosas, vectores progresivos), se ittera sobre las capas y se guarda con sufijo:

```python
profundidades = [3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23]

for prof in profundidades:
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(6, 6))

    vel_capa = df[df['profundidad'] == prof]['velocidad'].values
    dir_capa = df[df['profundidad'] == prof]['direccion'].values

    # ... graficar ...

    nombre = f'rosa_corrientes_{prof}m.png'
    fig.savefig(os.path.join(carpeta_figuras, nombre), dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  Figura guardada: {nombre}')
```

## Ciclo anual mensual

Para el informe de viento se genera una figura por mes con barras de percentiles:

```python
fig, ax = plt.subplots(figsize=(10, 5))

meses_nombres = ['Sep', 'Oct', 'Nov', 'Dic', 'Ene', 'Feb', 'Mar']
x = np.arange(len(meses_nombres))

ax.bar(x, promedios, color='steelblue', label='Promedio', zorder=3)
ax.vlines(x, p05, p95, color='navy', linewidth=2, label='P5–P95', zorder=4)
ax.scatter(x, maximos, color='firebrick', s=40, zorder=5, label='Máximo')

ax.set_xticks(x)
ax.set_xticklabels(meses_nombres)
ax.set_ylabel('Velocidad (m/s)')
ax.set_title('Ciclo anual de velocidad del viento')
ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(carpeta_figuras, 'ciclo_anual.png'), dpi=150, bbox_inches='tight')
plt.close(fig)
```

## Insertar figuras en Word

Una vez guardadas, las figuras se insertan en la plantilla Word desde el autoinforme. El proceso se describe en detalle en el capítulo de python-docx, pero el patrón básico es:

```python
from docx import Document
from docx.shared import Cm

doc = Document('plantilla.docx')

for parrafo in doc.paragraphs:
    if '[FIGURA_ROSA]' in parrafo.text:
        parrafo.clear()
        run = parrafo.add_run()
        run.add_picture('figuras_magnitud/rosa_corrientes_3m.png', width=Cm(12))
        break

doc.save('informe_final.docx')
```

## Figura multipanel para series de oleaje

El informe incluye una figura con tres paneles sincronizados (Hm0, Tm, Dm):

```python
fig, axes = plt.subplots(3, 1, figsize=(14, 8), sharex=True,
                          gridspec_kw={'hspace': 0.08})

# Panel 1: Altura Hm0
axes[0].plot(df.index, df['Hm0'], color='navy', linewidth=0.7)
axes[0].set_ylabel('Hm0 (m)')
axes[0].set_ylim(0, df['Hm0'].max() * 1.1)

# Panel 2: Periodo Tm
axes[1].plot(df.index, df['Tm'], color='teal', linewidth=0.7)
axes[1].set_ylabel('Tm (s)')

# Panel 3: Dirección Dm (puntos, no línea)
axes[2].scatter(df.index, df['Dm'], s=1, color='darkorange', alpha=0.6)
axes[2].set_ylabel('Dm (°)')
axes[2].set_ylim(0, 360)
axes[2].set_yticks([0, 90, 180, 270, 360])
axes[2].set_yticklabels(['N', 'E', 'S', 'O', 'N'])
axes[2].set_xlabel('Fecha')

# Formatear eje X con fechas
import matplotlib.dates as mdates
axes[2].xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
axes[2].xaxis.set_major_locator(mdates.MonthLocator())
plt.setp(axes[2].xaxis.get_majorticklabels(), rotation=30, ha='right')

fig.savefig('serie_oleaje.png', dpi=150, bbox_inches='tight')
plt.close(fig)
```

## GridSpec — layouts complejos

`subplots` crea paneles de igual tamaño. Cuando se necesita que algunos paneles sean más anchos o altos que otros, se usa `GridSpec`:

```python
import matplotlib.gridspec as gridspec

fig = plt.figure(figsize=(14, 8))
gs  = gridspec.GridSpec(2, 3, figure=fig, hspace=0.35, wspace=0.4)

# Panel grande a la izquierda (ocupa toda la columna 0)
ax_serie  = fig.add_subplot(gs[:, 0])    # filas 0:2, columna 0

# Dos paneles pequeños a la derecha
ax_hist   = fig.add_subplot(gs[0, 1:])  # fila 0, columnas 1-2
ax_rosa   = fig.add_subplot(gs[1, 1:], projection='polar')  # fila 1, columnas 1-2
```

```python
# Layout con ratios de tamaño explícitos
gs = gridspec.GridSpec(
    3, 1,
    height_ratios=[3, 1, 1],   # panel superior 3× más alto que los otros dos
    hspace=0.05
)
ax_vel = fig.add_subplot(gs[0])
ax_dir = fig.add_subplot(gs[1], sharex=ax_vel)
ax_qc  = fig.add_subplot(gs[2], sharex=ax_vel)
```

## Twin axes — dos escalas en el mismo panel

Cuando se grafican dos variables con distinta escala en el mismo panel (por ejemplo, velocidad y temperatura), se usa un eje secundario:

```python
fig, ax1 = plt.subplots(figsize=(12, 4))

# Eje izquierdo: velocidad
ax1.plot(df.index, df['velocidad'], color='steelblue', linewidth=0.8, label='Velocidad')
ax1.set_ylabel('Velocidad (m/s)', color='steelblue')
ax1.tick_params(axis='y', labelcolor='steelblue')

# Eje derecho: temperatura — comparte el eje X
ax2 = ax1.twinx()
ax2.plot(df.index, df['temperatura'], color='firebrick', linewidth=0.8,
         linestyle='--', label='Temperatura')
ax2.set_ylabel('Temperatura (°C)', color='firebrick')
ax2.tick_params(axis='y', labelcolor='firebrick')

# Leyenda combinada de ambos ejes
lineas1, labels1 = ax1.get_legend_handles_labels()
lineas2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lineas1 + lineas2, labels1 + labels2, loc='upper left')

fig.tight_layout()
```

!!! warning "Cuándo no usar twin axes"
    Dos ejes con distinta escala en el mismo panel pueden inducir correlaciones visuales falsas — el lector ve las curvas cruzarse o alinearse dependiendo de cómo se elijan las escalas. Preferir paneles separados con `sharex=True` cuando las variables son independientes. Reservar `twinx` para cuando la relación entre las dos variables es el punto central de la figura.

## Tamaño de figura para Word

El ancho de la zona de texto de un documento Word A4 con márgenes estándar es **~15.5 cm**. Para que las figuras queden alineadas y a escala correcta al insertarlas:

```python
# Figura de ancho completo (serie temporal, heatmap)
fig, ax = plt.subplots(figsize=(15.5/2.54, 5/2.54))   # cm → pulgadas (/2.54)

# Figura de media página (rosa, histograma)
fig, ax = plt.subplots(figsize=(7.5/2.54, 7.5/2.54))

# Guardar siempre con bbox_inches='tight' para no perder espacio en blanco
fig.savefig('figura.png', dpi=150, bbox_inches='tight', facecolor='white')
```

```python
# Función utilitaria para convertir cm a pulgadas
def cm(x): return x / 2.54

fig, ax = plt.subplots(figsize=(cm(15.5), cm(6)))
```

!!! tip "Cuándo usar `sharex=True`"
    En series temporales con múltiples variables (Hm0, Tm, Dm), `sharex=True` sincroniza el zoom y el paneo entre paneles. Si el usuario hace zoom en un panel en Spyder, todos los demás se actualizan juntos.
