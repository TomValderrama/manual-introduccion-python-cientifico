# Lectura de archivos

Un pipeline de datos científicos lee de múltiples fuentes y formatos: CSV de dataloggers, Excel de procesamiento, archivos `.mat` de MATLAB, y documentos Word para extracción de metadata.

## Archivos de texto y CSV

```python
import pandas as pd

# CSV estándar
df = pd.read_csv('viento.csv')

# Opciones comunes
df = pd.read_csv(
    'viento.csv',
    sep=';',                         # separador de columna
    decimal=',',                     # decimal con coma (datos europeos)
    skiprows=2,                      # saltar filas de encabezado
    encoding='latin-1',              # encoding para tildes
    parse_dates=['fecha'],           # convertir columna a datetime
    index_col='fecha',               # usar fecha como índice
    na_values=['-9999', 'N/A', '']  # valores a tratar como NaN
)
```

### Detectar encoding

Si el archivo tiene tildes y aparecen caracteres extraños, probar:

```python
for enc in ['utf-8', 'latin-1', 'cp1252']:
    try:
        df = pd.read_csv('archivo.csv', encoding=enc)
        print(f"Funciona con: {enc}")
        break
    except UnicodeDecodeError:
        continue
```

## Archivos Excel

```python
# Hoja por nombre
df = pd.read_excel('corrientes.xlsx', sheet_name='VELOCIDAD')

# Primera hoja
df = pd.read_excel('corrientes.xlsx', sheet_name=0)

# Leer todas las hojas
hojas = pd.read_excel('corrientes.xlsx', sheet_name=None)
# hojas es un dict: {'VELOCIDAD': df1, 'DIRECCION': df2, ...}

for nombre, df in hojas.items():
    print(f"Hoja '{nombre}': {df.shape}")
```

### Leer varias hojas de un Excel con múltiples pestañas

Cuando el Excel tiene hojas con nombres conocidos, conviene leerlas en un diccionario y manejar el caso de que alguna falte:

```python
hojas_requeridas = ['Datos', 'Estadisticas', 'Resumen']

datos = {}
for hoja in hojas_requeridas:
    try:
        datos[hoja] = pd.read_excel('procesamiento.xlsx', sheet_name=hoja)
    except Exception as e:
        print(f"  ! No se encontró la hoja '{hoja}': {e}")
```

## Archivos MATLAB (.mat)

Algunos instrumentos oceanográficos (sensores de oleaje, perfiladores) exportan datos en formato `.mat`. Se leen con `scipy.io`:

```python
from scipy.io import loadmat

mat = loadmat('datos_storm2.mat')

# mat es un diccionario con las variables del workspace de MATLAB
print(mat.keys())

# Extraer variables
Hm0 = mat['Hm0'].flatten()      # flatten convierte (N,1) → (N,)
Tp  = mat['Tp'].flatten()
tiempo = mat['time'].flatten()
```

### Convertir tiempo MATLAB a datetime de Python

MATLAB guarda el tiempo como número de días desde el 0-ene-0000. Para convertir a pandas:

```python
import pandas as pd
import numpy as np

def matlab_datenum_a_datetime(datenum):
    return pd.to_datetime(datenum - 719529, unit='D', origin='unix')

timestamps = matlab_datenum_a_datetime(tiempo)
```

## Archivos YAML

YAML es un formato de configuración más legible que JSON: no usa comillas en los strings simples, admite comentarios con `#`, y su indentación lo hace más natural para estructuras anidadas. Es el estándar para archivos de configuración de proyectos y pipelines.

```bash
conda install pyyaml    # o: pip install pyyaml
```

```python
import yaml

# Leer
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)    # safe_load evita ejecución de código arbitrario

empresa = config['empresa']
ruta    = config['rutas']['datos']

# Guardar
with open('config.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
```

### config.yaml para un proyecto oceanográfico

```yaml
# Configuración del proyecto — editar aquí, no en el código
proyecto:
  empresa:  "Compas Marine"
  centro:   "Los Vilos"
  campana:  "oct2025"

rutas:
  datos:    "/mnt/c/Users/Usuario/proyectos/los_vilos/datos"
  figuras:  "/mnt/c/Users/Usuario/proyectos/los_vilos/figuras"
  informe:  "/mnt/c/Users/Usuario/proyectos/los_vilos/informe"

instrumentos:
  adcp:
    archivo:       "corrientes_adcp.csv"
    profundidades: [3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23]
  viento:
    archivo:       "viento_boya.csv"

parametros:
  velocidad_max_corte: 1.5    # m/s — valores sobre este umbral son outliers
  suavizado_horas:     1      # ventana de rolling en horas
```

```python
# Usar en el pipeline
import yaml
from pathlib import Path

with open('config.yaml', 'r', encoding='utf-8') as f:
    cfg = yaml.safe_load(f)

ruta_datos  = Path(cfg['rutas']['datos'])
prof_adcp   = cfg['instrumentos']['adcp']['profundidades']
vel_max     = cfg['parametros']['velocidad_max_corte']

df = pd.read_csv(ruta_datos / cfg['instrumentos']['adcp']['archivo'])
df = df[df['velocidad'] < vel_max]
```

La ventaja sobre rutas hardcodeadas: el mismo script corre para cualquier proyecto cambiando solo el `config.yaml`. No hay que tocar el código.

## Archivos JSON

```python
import json

# Leer
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

empresa = config['empresa']

# Guardar
with open('estado.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)
```

## Archivos de texto plano

```python
# Leer completo
with open('notas.txt', 'r', encoding='utf-8') as f:
    contenido = f.read()

# Leer línea por línea
with open('log.txt', 'r') as f:
    for linea in f:
        print(linea.strip())

# Escribir
with open('resultado.txt', 'w', encoding='utf-8') as f:
    f.write("Velocidad máxima: 0.6 m/s\n")
    f.write("Profundidad: 7 m\n")
```

## Buscar archivos con glob y os

En el pipeline es frecuente buscar archivos por patrón sin saber el nombre exacto:

```python
import glob
import os

# Todos los Excel en una carpeta
archivos = glob.glob('/ruta/carpeta/*.xlsx')

# Recursivo (busca en subcarpetas también)
archivos = glob.glob('/ruta/**/*.xlsx', recursive=True)

# Filtrar con condición
excels_corrientes = [
    f for f in glob.glob('/ruta/*.xlsx')
    if 'corriente' in f.lower()
]

# Listar archivos y carpetas
os.listdir('/ruta/carpeta')

# Verificar si existe
os.path.exists('/ruta/archivo.csv')

# Construir rutas de forma segura (funciona en Windows y Linux)
ruta = os.path.join('/ruta/base', 'subcarpeta', 'archivo.csv')
```

## Documentos Word (.docx)

Python-docx permite leer texto desde documentos Word, útil para extraer metadata de informes anteriores:

```python
from docx import Document

doc = Document('informe.docx')

# Leer todos los párrafos
for parrafo in doc.paragraphs:
    if parrafo.text.strip():
        print(parrafo.text)

# Leer tablas
for tabla in doc.tables:
    for fila in tabla.rows:
        celdas = [celda.text for celda in fila.cells]
        print(celdas)
```

### Leer .docx sin python-docx (XML directo)

Para extraer texto con más control, el `.docx` es en realidad un archivo ZIP con XML adentro:

```python
import zipfile
import re

def extraer_texto_docx(ruta):
    with zipfile.ZipFile(ruta) as z:
        xml = z.read('word/document.xml').decode('utf-8')
    # Eliminar etiquetas XML
    texto = re.sub(r'<[^>]+>', ' ', xml)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto
```

## Manejo de rutas con pathlib

La librería `pathlib` ofrece una forma más moderna de trabajar con rutas:

```python
from pathlib import Path

carpeta = Path('/ruta/a/mis/datos')
archivo = carpeta / 'campana_oct2025' / 'corrientes.csv'

archivo.exists()        # True/False
archivo.suffix          # '.csv'
archivo.stem            # 'corrientes'
archivo.parent          # carpeta Los Vilos
archivo.name            # 'corrientes.csv'

# Listar archivos
list(carpeta.glob('*.xlsx'))
list(carpeta.rglob('*.csv'))   # recursivo
```

!!! warning "Rutas en Windows desde WSL"
    Al usar Python desde WSL (Windows Subsystem for Linux), las rutas de Windows se acceden como `/mnt/c/...`. Las rutas con espacios deben ir entre comillas o manejarse con `Path`:
    ```python
    ruta = Path('/mnt/c/Users/Usuario/Mi Carpeta/archivo.csv')
    ```
