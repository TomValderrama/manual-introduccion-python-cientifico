# Rosas de viento y diagramas polares

Las rosas de dirección y los diagramas polares son las figuras más características del análisis oceanográfico. Se usan para visualizar la distribución de velocidades y direcciones del viento, corrientes y oleaje.

## Rosa de viento con windrose

La librería `windrose` genera rosas directamente desde arrays de velocidad y dirección:

```python
from windrose import WindroseAxes
import matplotlib.pyplot as plt
import numpy as np

fig = plt.figure(figsize=(7, 7))
ax = WindroseAxes.from_ax(fig=fig)

ax.bar(
    direccion,           # array de direcciones (°, convención meteorológica: FROM)
    velocidad,           # array de velocidades (m/s)
    normed=True,         # mostrar como porcentaje
    opening=0.9,
    edgecolor='white',
    bins=[0, 2, 4, 6, 8, 10],   # intervalos de velocidad
    cmap=plt.cm.YlOrRd
)

ax.set_legend(title='Velocidad (m/s)', loc='lower right')
ax.set_title('Rosa de viento — Los Vilos')

fig.savefig('rosa_viento.png', dpi=150, bbox_inches='tight')
plt.close(fig)
```

## Rosa de corrientes (sin windrose)

Para corrientes se suele hacer una rosa manual usando proyección polar de Matplotlib, con más control sobre el diseño:

```python
import matplotlib.pyplot as plt
import numpy as np

def rosa_corrientes(direcciones, velocidades, titulo='', ax=None):
    """Rosa de corrientes en 8 octantes."""
    octantes = np.arange(0, 360, 45)
    etiquetas = ['N', 'NE', 'E', 'SE', 'S', 'SO', 'O', 'NO']
    colores_vel = plt.cm.Blues(np.linspace(0.3, 1.0, 4))
    bins_vel = [0, 0.05, 0.1, 0.2, np.inf]
    labels_vel = ['0–0.05', '0.05–0.1', '0.1–0.2', '>0.2']

    if ax is None:
        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(6, 6))

    # Orientar norte arriba, sentido horario
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)

    ancho = np.radians(45) * 0.85
    bottom = np.zeros(8)

    for i, (vmin, vmax) in enumerate(zip(bins_vel[:-1], bins_vel[1:])):
        mask = (velocidades >= vmin) & (velocidades < vmax)
        conteos = np.zeros(8)
        for j, oct in enumerate(octantes):
            mask_dir = (direcciones >= oct - 22.5) & (direcciones < oct + 22.5)
            conteos[j] = np.sum(mask & mask_dir)

        pct = conteos / len(velocidades) * 100
        theta = np.radians(octantes)
        ax.bar(theta, pct, width=ancho, bottom=bottom,
               color=colores_vel[i], label=labels_vel[i], edgecolor='white', linewidth=0.5)
        bottom += pct

    ax.set_xticks(np.radians(octantes))
    ax.set_xticklabels(etiquetas)
    ax.set_title(titulo, pad=15)
    ax.legend(title='Vel (m/s)', loc='lower right', bbox_to_anchor=(1.3, -0.1))

    return ax
```

## Diagrama polar de dispersión

Muestra la distribución conjunta de velocidad y dirección, con cada punto representando un registro:

```python
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(7, 7))
ax.set_theta_zero_location('N')
ax.set_theta_direction(-1)

sc = ax.scatter(
    np.radians(direccion),
    velocidad,
    c=velocidad,           # color según velocidad
    cmap='YlOrRd',
    s=3,
    alpha=0.4
)

# Marcar el máximo
idx_max = np.argmax(velocidad)
ax.scatter(np.radians(direccion[idx_max]), velocidad[idx_max],
           c='red', s=80, zorder=5, label=f'Máx: {velocidad[idx_max]:.2f} m/s')

fig.colorbar(sc, ax=ax, label='Velocidad (m/s)', shrink=0.7)
ax.set_title('Diagrama polar de dispersión')
ax.legend(loc='lower right')
```

## Vector progresivo

El vector progresivo acumula el desplazamiento (U, V) a lo largo del tiempo, mostrando la trayectoria resultante:

```python
def vector_progresivo(velocidad, direccion, dt_horas=0.167):
    """
    Calcula el vector progresivo.
    dt_horas: intervalo entre registros en horas (10 min = 0.167 h)
    """
    u = velocidad * np.sin(np.radians(direccion))
    v = velocidad * np.cos(np.radians(direccion))

    # Desplazamiento acumulado en km
    x = np.cumsum(u * dt_horas * 3.6)   # m/s × h × 3.6 → km
    y = np.cumsum(v * dt_horas * 3.6)

    return x, y

# Graficar
x, y = vector_progresivo(vel_prof, dir_prof)

fig, ax = plt.subplots(figsize=(6, 6))
ax.plot(x, y, color='steelblue', linewidth=0.8)
ax.plot(0, 0, 'go', markersize=8, label='Inicio')
ax.plot(x[-1], y[-1], 'r*', markersize=12, label=f'Final: {np.sqrt(x[-1]**2+y[-1]**2):.1f} km')
ax.axhline(0, color='gray', linewidth=0.5)
ax.axvline(0, color='gray', linewidth=0.5)
ax.set_xlabel('Desplazamiento E–O (km)')
ax.set_ylabel('Desplazamiento N–S (km)')
ax.set_aspect('equal')
ax.legend()
ax.set_title('Vector progresivo')
```

## Patrón diurno

Gráfico de líneas por mes mostrando el ciclo horario de la velocidad:

```python
import pandas as pd

# df tiene índice DatetimeIndex
patron = df.groupby([df.index.month, df.index.hour])['velocidad'].mean().unstack(level=0)
# patron: filas=hora (0–23), columnas=mes (1–12)

nombres_meses = {9:'Sep', 10:'Oct', 11:'Nov', 12:'Dic', 1:'Ene', 2:'Feb', 3:'Mar'}
colores_meses = plt.cm.tab10(np.linspace(0, 1, 12))

fig, ax = plt.subplots(figsize=(10, 5))

for mes, col in zip(patron.columns, colores_meses):
    ax.plot(patron.index, patron[mes], label=nombres_meses.get(mes, mes),
            color=col, linewidth=1.2)

# Promedio global
ax.plot(patron.index, patron.mean(axis=1),
        color='black', linewidth=2.5, linestyle='--', label='Promedio global')

ax.set_xlabel('Hora del día (UTC-3)')
ax.set_ylabel('Velocidad media (m/s)')
ax.set_title('Patrón diurno de velocidad del viento')
ax.set_xticks(range(0, 24, 2))
ax.set_xticklabels([f'{h:02d}:00' for h in range(0, 24, 2)], rotation=45)
ax.legend(ncol=4, fontsize=8)
ax.grid(True, alpha=0.3)
fig.tight_layout()
```

!!! tip "Convención de dirección"
    En meteorología la dirección indica **desde dónde** viene el viento (FROM). En oceanografía de corrientes, la convención es **hacia dónde** va (TO). Al graficar rosas, hay que tener claro cuál convención se está usando para que la rosa tenga sentido físico.
