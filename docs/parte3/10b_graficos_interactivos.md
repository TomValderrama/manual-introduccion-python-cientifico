# Gráficos interactivos y el event loop

Matplotlib puede mostrar figuras estáticas, abrir ventanas interactivas con zoom y pan, responder a clics del usuario, y generar animaciones. Cada uno de estos modos tiene restricciones técnicas que conviene entender antes de mezclarlos en un script.

## El event loop — por qué existe la limitación

Una ventana de escritorio (Qt, Tk, cualquier GUI) necesita estar constantemente "escuchando" eventos: clics, redimensionado, movimiento del mouse. Este proceso de escucha continua es el **event loop** — un bucle que corre indefinidamente hasta que se cierra la ventana.

Python es de un solo hilo por defecto. Cuando el event loop de una ventana está corriendo, Python no puede ejecutar código al mismo tiempo. Por eso `plt.show()` en un script normal bloquea: hasta que el usuario cierra la figura, el script no avanza.

En Spyder e IPython esto se resuelve de otra forma: el kernel de IPython corre un event loop propio que puede procesar eventos de ventana en paralelo con la ejecución del código. Es lo que permite que escribas en la consola mientras una figura de Tkinter está abierta.

## Los backends de matplotlib

El **backend** es el motor que matplotlib usa para renderizar y mostrar figuras. Se divide en dos categorías:

| Backend | Tipo | Descripción |
|---|---|---|
| `Agg` | No interactivo | Renderiza a memoria. Sin ventana. Solo para guardar archivos. |
| `TkAgg` | Interactivo | Ventana Tkinter. Estable en Spyder. |
| `Qt5Agg` | Interactivo | Ventana Qt5. Sin conflicto en VSCode; puede interferir en Spyder. |
| `inline` | IPython | Renderiza a imagen estática embebida en la consola. No es un backend real — es un hook de IPython sobre Agg. |

```python
# Ver el backend activo
import matplotlib
matplotlib.get_backend()   # 'module://matplotlib_inline.backend_inline' en Spyder inline

# Cambiar desde la consola IPython (antes de crear cualquier figura)
%matplotlib tk      # Tkinter interactivo
%matplotlib qt5     # Qt5 interactivo
%matplotlib inline  # volver a inline

# En un script .py fuera de IPython, antes de importar pyplot:
import matplotlib
matplotlib.use('Agg')    # solo para guardar, sin ventana
import matplotlib.pyplot as plt
```

## El problema de mezclar backends en un script

El backend se inicializa la primera vez que se importa `matplotlib.pyplot`. Una vez activo, **no se puede cambiar limpiamente en la misma sesión**: matplotlib lanza una advertencia y el comportamiento es impredecible.

```python
# Esto no funciona bien:
%matplotlib inline
import matplotlib.pyplot as plt
plt.plot([1, 2, 3])     # figura inline — OK

%matplotlib tk          # advertencia: backend ya inicializado
plt.figure()            # puede no abrir ventana, o abrirla sin event loop
```

**Solución práctica**: decidir un backend al inicio y no cambiarlo. Si se necesitan figuras interactivas Y figuras guardadas en el mismo script, usar el backend interactivo y guardar con `fig.savefig()` — eso funciona desde cualquier backend, incluido Tk y Qt5.

```python
# Patrón correcto: backend interactivo, guardar explícitamente
%matplotlib tk

fig, ax = plt.subplots()
ax.plot(df['velocidad'])
plt.show()                              # ventana interactiva para explorar

fig.savefig('velocidad.png', dpi=150)   # guardar también — funciona igual
plt.close(fig)
```

## plt.ion() — modo interactivo sin bloquear

`plt.ion()` activa el modo interactivo: las figuras se actualizan inmediatamente cuando se modifica el gráfico, sin necesidad de llamar a `plt.show()`. El script sigue corriendo sin que la ventana bloquee la ejecución.

```python
%matplotlib tk
import matplotlib.pyplot as plt
import numpy as np

plt.ion()   # activar modo interactivo

fig, ax = plt.subplots()
linea, = ax.plot([], [])
ax.set_xlim(0, 100)
ax.set_ylim(-1, 1)

# Actualizar la figura en un loop — simula datos llegando en tiempo real
for i in range(100):
    x = np.arange(i)
    y = np.sin(x * 0.3)
    linea.set_data(x, y)
    ax.relim()
    fig.canvas.draw()
    plt.pause(0.05)   # procesar eventos de ventana y esperar 50 ms

plt.ioff()   # volver al modo normal
```

`plt.pause(t)` es fundamental en este patrón: le da tiempo al event loop de la ventana para procesar eventos (zoom, clic, redimensionado) y luego devuelve el control al script. Sin `pause`, la ventana se congela.

## matplotlib.widgets — interactividad básica dentro del canvas

Los widgets de matplotlib viven dentro del canvas de la figura — no requieren construir una aplicación Qt o Tk completa. Son suficientes para ajustar parámetros de forma interactiva en un script exploratorio.

```python
%matplotlib tk
import matplotlib.pyplot as plt
import matplotlib.widgets as widgets
import numpy as np

# Serie temporal de ejemplo
t   = np.linspace(0, 10, 500)
vel = np.sin(2 * np.pi * t)

fig, ax = plt.subplots(figsize=(10, 5))
plt.subplots_adjust(bottom=0.25)   # espacio para el slider

linea, = ax.plot(t, vel)
ax.set_xlabel('Tiempo (h)')
ax.set_ylabel('Velocidad (m/s)')

# Slider para cambiar la frecuencia
ax_slider = plt.axes([0.2, 0.08, 0.6, 0.04])
slider = widgets.Slider(ax_slider, 'Frecuencia (Hz)', 0.1, 5.0, valinit=1.0)

def actualizar(valor):
    freq = slider.val
    linea.set_ydata(np.sin(2 * np.pi * freq * t))
    fig.canvas.draw_idle()

slider.on_changed(actualizar)
plt.show()
```

Otros widgets disponibles: `Button`, `CheckButtons` (checkboxes), `RadioButtons`, `TextBox`, `RectangleSelector` (seleccionar región con el mouse).

**Limitación**: los widgets de matplotlib son básicos. No hay menús, ni cuadros de diálogo para abrir archivos, ni tablas. Para eso se necesita PyQt5.

## FuncAnimation — animaciones

`FuncAnimation` crea una animación llamando una función de actualización para cada frame. Puede mostrarse en vivo o guardarse como GIF o MP4.

```python
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

fig, ax = plt.subplots(figsize=(10, 4))
ax.set_xlim(0, 4 * np.pi)
ax.set_ylim(-1.5, 1.5)
ax.set_xlabel('Tiempo')
ax.set_ylabel('Velocidad (m/s)')

linea, = ax.plot([], [], linewidth=1.5)
x = np.linspace(0, 4 * np.pi, 300)

def init():
    linea.set_data([], [])
    return (linea,)

def update(frame):
    y = np.sin(x - 0.05 * frame)   # ola que avanza
    linea.set_data(x, y)
    return (linea,)

ani = animation.FuncAnimation(
    fig,
    update,
    frames=200,
    init_func=init,
    interval=50,    # ms entre frames
    blit=True       # solo redibuja lo que cambió — más eficiente
)

plt.show()
```

### Guardar la animación

```python
# GIF — requiere pillow: pip install pillow
ani.save('corriente.gif', writer='pillow', fps=20, dpi=100)

# MP4 — requiere ffmpeg instalado en el sistema
ani.save('corriente.mp4', writer='ffmpeg', fps=30, dpi=150)
```

### Ejemplo oceanográfico: evolución de perfil vertical

```python
fig, ax = plt.subplots(figsize=(4, 8))
ax.set_xlim(0, 1)
ax.set_ylim(-25, 0)
ax.set_xlabel('Velocidad (m/s)')
ax.set_ylabel('Profundidad (m)')
ax.invert_yaxis()

profundidades = np.array([-3, -5, -7, -9, -11, -13, -15, -17, -19, -21, -23])
linea, = ax.plot([], profundidades, 'o-', color='steelblue')
titulo = ax.set_title('')

def update(frame):
    # Perfil que oscila con la marea (ejemplo sintético)
    vel = 0.3 + 0.2 * np.sin(2 * np.pi * frame / 60) * np.exp(profundidades / 10)
    linea.set_xdata(vel)
    titulo.set_text(f'Hora: {frame:03d}')
    return linea, titulo

ani = animation.FuncAnimation(fig, update, frames=120, interval=100, blit=True)
plt.tight_layout()
plt.show()
```

## PyQt5 — herramientas con interfaz propia

Cuando `matplotlib.widgets` no es suficiente — se necesita navegar entre archivos, tener checkboxes y botones con lógica compleja, o mostrar una tabla junto con el gráfico — se puede embeber matplotlib dentro de una ventana Qt5 construida a medida.

Este nivel de desarrollo es más complejo y está fuera del scope del pipeline de corrientes, pero aparece cuando se construyen herramientas reutilizables: un editor de control de calidad de ADCP, una interfaz para digitalizar batimetría, un visor de salidas de CROCO.

La estructura básica:

```python
import sys
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget,
                              QVBoxLayout, QPushButton, QLabel)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Visor de corrientes')
        self.resize(900, 600)

        # Widget central con layout vertical
        central = QWidget()
        layout  = QVBoxLayout(central)
        self.setCentralWidget(central)

        # Canvas de matplotlib embebido
        fig = Figure(figsize=(8, 4))
        self.canvas = FigureCanvasQTAgg(fig)
        self.ax = fig.add_subplot(111)
        layout.addWidget(self.canvas)

        # Botón de Qt
        boton = QPushButton('Actualizar')
        boton.clicked.connect(self.actualizar_figura)
        layout.addWidget(boton)

        self.label = QLabel('Listo.')
        layout.addWidget(self.label)

        self.actualizar_figura()

    def actualizar_figura(self):
        t   = np.linspace(0, 24, 144)
        vel = 0.3 + 0.15 * np.sin(2 * np.pi * t / 12.4)   # ciclo mareal
        self.ax.clear()
        self.ax.plot(t, vel, color='steelblue')
        self.ax.set_xlabel('Hora')
        self.ax.set_ylabel('Velocidad (m/s)')
        self.canvas.draw()
        self.label.setText(f'Velocidad máxima: {vel.max():.3f} m/s')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec_())
```

**Nota sobre Spyder**: este script debe correrse desde la terminal o desde VSCode, no desde la consola de Spyder. `QApplication` crea su propia instancia de Qt y entra en su propio event loop (`app.exec_()`), lo que entra en conflicto con el event loop Qt que ya usa Spyder. Desde la terminal funciona perfectamente.

```bash
python visor_corrientes.py
```

## Cuándo usar cada enfoque

| Necesidad | Solución |
|---|---|
| Explorar datos, hacer zoom y pan | Backend Tk o Qt5, `%matplotlib tk` |
| Guardar figuras para informe | `Agg` o cualquier backend + `savefig()` |
| Ajustar parámetros en vivo con un slider | `matplotlib.widgets` |
| Mostrar evolución temporal / animación | `FuncAnimation` → guardar GIF/MP4 |
| Herramienta reutilizable con botones y menús | PyQt5 + FigureCanvasQTAgg |
| Script automático sin display (servidor) | `matplotlib.use('Agg')` antes del import |

## Reglas prácticas

1. **Elegir un backend al inicio del script y no cambiarlo.** Si se necesita guardar y también ver la figura, usar backend interactivo y llamar a `savefig()` — funciona igual.

2. **Separar scripts de exploración de scripts de producción.** El script que genera las figuras del informe siempre usa `Agg` (o simplemente `savefig` con cualquier backend) y corre sin intervención. El script de exploración usa Tk para inspeccionar.

3. **`plt.show()` bloquea en scripts fuera de IPython.** Si el script tiene código después de `plt.show()`, ese código no corre hasta que el usuario cierra la ventana. Usar `plt.ion()` + `plt.pause()` para evitar el bloqueo.

4. **PyQt5 no va en Spyder — va en un script independiente.** La aplicación Qt crea su propia `QApplication`; si Spyder ya creó una, el conflicto produce cierres inesperados o que la ventana no aparezca.
