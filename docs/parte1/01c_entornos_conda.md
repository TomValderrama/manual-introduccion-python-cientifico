# Entornos virtuales con conda

## ¿Qué es un entorno virtual?

Un entorno virtual es una instalación aislada de Python con sus propios paquetes. Sin entornos, todos los proyectos comparten los mismos paquetes instalados en el Python global — lo que inevitablemente genera conflictos: el proyecto A necesita numpy 1.24, el proyecto B necesita numpy 2.0, y no pueden coexistir en la misma instalación.

Con un entorno por proyecto, cada uno tiene sus propias versiones y los conflictos desaparecen. También permite compartir exactamente qué versiones se usaron para producir un análisis — lo que hace el trabajo reproducible.

## conda vs pip

Anaconda incluye dos gestores de paquetes:

| | conda | pip |
|---|---|---|
| Qué instala | Python + librerías C/Fortran | Paquetes Python |
| Resuelve dependencias binarias | Sí | No |
| Crea entornos virtuales | `conda create` | `venv` |
| Fuente de paquetes | Anaconda / conda-forge | PyPI |

Para paquetes científicos — NumPy, SciPy, GDAL, rasterio — conda maneja mejor las dependencias compiladas. Para paquetes de Python puro que no están en conda, pip funciona igual.

**Regla práctica**: instalar con conda lo que esté disponible; usar pip para el resto. Evitar mezclar en el mismo entorno si es posible.

## Crear y activar un entorno

```bash
# Crear un entorno con Python 3.11
conda create -n oceanografia python=3.11

# Activar
conda activate oceanografia

# El prompt cambia para indicar qué entorno está activo:
# (oceanografia) $
```

Una vez activado, todos los `conda install` y `pip install` afectan solo a ese entorno — el sistema global queda intacto.

```bash
# Desactivar (volver al entorno base)
conda deactivate
```

## Instalar paquetes

```bash
# Instalar varios paquetes a la vez
conda install numpy pandas matplotlib scipy

# conda-forge tiene versiones más actualizadas de paquetes geoespaciales
conda install -c conda-forge xarray rasterio geopandas

# pip para lo que no está en conda
pip install python-docx pytesseract tqdm pyyaml

# Ver qué hay instalado en el entorno activo
conda list
```

## Listar y eliminar entornos

```bash
conda env list                          # ver todos los entornos
conda env remove -n nombre_entorno      # eliminar un entorno completo
```

## Exportar e importar entornos

La forma de hacer un análisis reproducible y compartible es exportar el entorno:

```bash
# Exportar el entorno activo
conda env export > environment.yml

# Recrear el entorno exacto en otro equipo
conda env create -f environment.yml
conda activate oceanografia
```

El archivo `environment.yml` resultante se ve así:

```yaml
name: oceanografia
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - numpy=2.0.1
  - pandas=2.2.2
  - matplotlib=3.9.1
  - scipy=1.13.1
  - xarray=2024.7.0
  - rasterio=1.3.10
  - pip:
    - python-docx==1.1.2
    - tqdm==4.66.4
    - pyyaml==6.0.1
```

Compartir este archivo con un colaborador garantiza que tiene exactamente las mismas versiones. Es más confiable que una lista de `pip install` en un README.

## El entorno base — por qué no instalar todo ahí

Anaconda viene con un entorno `base` preinstalado con Python y los paquetes científicos más comunes. Es tentador instalar todo ahí, pero tiene una desventaja: cada paquete nuevo puede romper la compatibilidad con los que ya estaban. Después de varios meses de instalaciones, el entorno base se vuelve inconsistente y difícil de reparar.

```bash
# Mal: instalar todo en base
conda install nuevo_paquete   # puede romper numpy o pandas que ya estaban

# Bien: crear un entorno separado
conda create -n mi_proyecto python=3.11
conda activate mi_proyecto
conda install nuevo_paquete   # solo afecta este entorno
```

**Recomendación**: reservar `base` solo para conda mismo. Un entorno para el trabajo de este manual, otro para proyectos distintos si tienen dependencias incompatibles.

## Actualizar paquetes

```bash
# Actualizar un paquete específico
conda update numpy

# Actualizar todos los paquetes del entorno activo
conda update --all

# Actualizar conda mismo (desde el entorno base)
conda update conda
```

## Conectar el entorno a Spyder

Spyder usa su propio intérprete por defecto. Para que use el entorno `oceanografia`:

1. Con el entorno activo, instalar el kernel que Spyder necesita:
   ```bash
   conda activate oceanografia
   conda install spyder-kernels
   ```
2. En Spyder: **Tools → Preferences → Python interpreter → Use the following interpreter**
3. Pegar la ruta del Python del entorno:
   - Windows: `C:\Users\Usuario\anaconda3\envs\oceanografia\python.exe`
   - Linux/WSL: `/home/usuario/anaconda3/envs/oceanografia/bin/python`
4. Reiniciar el kernel de Spyder (`Ctrl+.`).

El Variable Explorer y la consola IPython de Spyder ahora usan los paquetes del entorno, no los del sistema.

## Conectar el entorno a VSCode

`Ctrl+Shift+P` → **Python: Select Interpreter** → elegir `oceanografia` de la lista. VSCode detecta automáticamente los entornos conda instalados.

## Entorno recomendado para este manual

Para seguir todos los capítulos del manual sin problemas de dependencias:

```bash
conda create -n oceanografia python=3.11
conda activate oceanografia

conda install -c conda-forge numpy pandas matplotlib scipy xarray rasterio geopandas

pip install python-docx pytesseract tqdm pyyaml
```

```bash
# Guardar para compartir o reproducir
conda env export > environment.yml
```

!!! tip "Reinstalación limpia"
    Si el entorno queda inconsistente después de muchas instalaciones y desinstalaciones, la solución más rápida es eliminarlo y recrearlo desde el `environment.yml`: `conda env remove -n oceanografia` y luego `conda env create -f environment.yml`. Tarda unos minutos pero garantiza un entorno limpio.
