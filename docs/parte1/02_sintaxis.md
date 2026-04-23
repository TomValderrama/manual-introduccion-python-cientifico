# Sintaxis básica

Python es un lenguaje de tipado dinámico e indentado. No necesita declarar tipos de variables ni usar llaves `{}` para delimitar bloques — la estructura del código se define por la indentación.

## Variables y tipos

Python detecta el tipo de una variable automáticamente al asignarla. No es necesario declararlo. Los tipos fundamentales son:

### float — número decimal

Representa cualquier número con parte decimal. Internamente usa 64 bits (doble precisión), lo que da ~15 dígitos significativos de precisión.

```python
velocidad   = 3.5       # float
temperatura = -1.8      # float (puede ser negativo)
proporcion  = 0.73      # float entre 0 y 1

type(velocidad)   # <class 'float'>
```

Se usa para mediciones físicas: velocidades, temperaturas, coordenadas, profundidades. Cualquier número que pueda tener decimales debe ser float.

!!! warning "Precisión de float"
    Los floats tienen un error de representación inherente. `0.1 + 0.2` en Python da `0.30000000000000004`, no `0.3`. Esto rara vez afecta el análisis de datos, pero sí puede causar sorpresas en comparaciones exactas. Usar `round()` o `np.isclose()` en vez de `==` para comparar floats.

### int — número entero

Número sin parte decimal. En Python 3 no tiene límite de tamaño.

```python
n_muestras  = 186       # int
profundidad = 7         # int (metros exactos)
indice      = 0         # int — los índices siempre son int

type(n_muestras)   # <class 'int'>
```

Se usa para contadores, índices, cantidades discretas (número de archivos, de celdas, de meses).

```python
# La división entre ints en Python 3 siempre da float
7 / 2      # 3.5   (float)
7 // 2     # 3     (int — división entera)
7 % 2      # 1     (int — resto)
```

### str — texto

Secuencia de caracteres. Se define con comillas simples o dobles (equivalentes).

```python
nombre_proyecto = "Los Vilos Oct 2025"
unidad          = 'm/s'
ruta            = r'C:\Users\Tomas\datos.csv'   # r"..." ignora las barras invertidas
```

### bool — booleano

Solo dos valores posibles: `True` o `False`. Es un caso especial de int (`True == 1`, `False == 0`).

```python
datos_validos = True
es_negativo   = velocidad < 0   # bool resultado de una comparación

# Se usa en condiciones
if datos_validos:
    procesar(df)
```

### None — ausencia de valor

Representa "sin valor". Equivalente a `NULL` en otras lenguas.

```python
resultado = None   # aún no calculado

# Verificar si algo es None
if resultado is None:
    print("Aún no hay resultado")
```

### Resumen y conversión entre tipos

```python
# Verificar tipo
type(3.5)     # <class 'float'>
type(23)      # <class 'int'>
type("texto") # <class 'str'>
type(True)    # <class 'bool'>

# Convertir
int(3.9)      # 3     — trunca, no redondea
float(23)     # 23.0
str(186)      # '186'
int("23")     # 23    — solo si el string es un número válido
bool(0)       # False — 0 es falso, cualquier otro número es True
bool("")      # False — string vacío es falso
```

### ¿Cuándo importa el tipo?

```python
# Concatenar string con número da error
nombre = "Profundidad: " + 7          # TypeError
nombre = "Profundidad: " + str(7)     # OK: "Profundidad: 7"
nombre = f"Profundidad: {7}"          # OK con f-string (convierte automático)

# Operaciones entre int y float dan float
3 + 1.5    # 4.5 (float)
7 * 2.0    # 14.0 (float)
```

## Strings (texto)

```python
empresa = "Compas Marine"
centro  = "Los Vilos"

# Concatenación
titulo = empresa + " — " + centro

# f-strings (la forma moderna y más legible)
titulo = f"{empresa} — {centro}"

# Formateo con decimales
promedio = 3.93
texto = f"Velocidad promedio: {promedio:.2f} m/s"
# → "Velocidad promedio: 3.93 m/s"

# Métodos útiles
"Los Vilos".upper()       # 'LOS VILOS'
"  texto  ".strip()       # 'texto'
"a,b,c".split(",")        # ['a', 'b', 'c']
"corrientes".replace("e", "a")  # 'corriantes'
```

## Listas

Las listas almacenan secuencias de elementos de cualquier tipo:

```python
profundidades = [3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23]
meses = ["sep", "oct", "nov", "dic", "ene", "feb", "mar"]

# Acceso por índice (empieza en 0)
profundidades[0]    # 3
profundidades[-1]   # 23 (último)
profundidades[2:5]  # [7, 9, 11] (slice)

# Operaciones
len(profundidades)          # 11
profundidades.append(25)    # agrega al final
profundidades.sort()        # ordena en lugar
sum(profundidades)          # suma
```

## Tuplas

Las tuplas son secuencias **inmutables**: se definen igual que una lista pero con paréntesis, y no se pueden modificar después de creadas.

```python
coordenadas = (-31.9, -71.5)           # (lat, lon)
rango       = (0, 23)                  # profundidad mínima y máxima
rgb         = (30, 144, 255)           # color fijo

# Acceso — igual que lista
coordenadas[0]    # -31.9
coordenadas[-1]   # -71.5
```

**¿Por qué no simplemente usar una lista?** La inmutabilidad comunica intención: si algo es una tupla, el lector del código sabe que ese valor no va a cambiar. También tienen otro uso frecuente: las funciones que devuelven múltiples valores en Python devuelven una tupla.

```python
def estadisticas(datos):
    return np.mean(datos), np.std(datos)   # devuelve tupla

media, std = estadisticas(vel)   # desempaquetado automático
```

```python
# Diferencia clave con lista
lista = [1, 2, 3]
lista[0] = 99       # OK — las listas son mutables

tupla = (1, 2, 3)
tupla[0] = 99       # TypeError: 'tuple' object does not support item assignment
```

Se usa para: coordenadas geográficas, rangos fijos de profundidad o tiempo, pares clave-valor, y cualquier conjunto de valores relacionados que no deba cambiar.

## Diccionarios

Los diccionarios almacenan pares clave-valor. Son muy usados para configuración:

```python
config = {
    "empresa": "Compas Marine",
    "centro":  "Los Vilos",
    "lat":     -31.9,
    "lon":     -71.5,
    "prof_max": 23
}

# Acceso
config["empresa"]          # "Compas Marine"
config.get("lat", None)    # -31.9 (con valor por defecto si no existe)

# Modificar
config["prof_max"] = 25

# Iterar
for clave, valor in config.items():
    print(f"{clave}: {valor}")
```

## Indentación

Python usa la indentación (4 espacios) para delimitar bloques. No hay llaves ni `end`:

```python
# Correcto
if velocidad > 0.5:
    print("Velocidad alta")
    print("Revisar datos")

# Error — la indentación inconsistente produce IndentationError
if velocidad > 0.5:
print("Velocidad alta")   # ← falta indentación
```

## Comentarios

```python
# Comentario de una línea

velocidad_max = 0.6  # m/s — comentario al final de línea

"""
Comentario de
múltiples líneas
(también se usa como docstring de funciones)
"""
```

## Operadores

```python
# Aritméticos
3 + 2     # 5
10 / 3    # 3.333...
10 // 3   # 3 (división entera)
10 % 3    # 1 (módulo / resto)
2 ** 3    # 8 (potencia)

# Comparación
5 > 3     # True
5 == 5    # True (igualdad, no asignación)
5 != 4    # True

# Lógicos
True and False   # False
True or False    # True
not True         # False

# Útil con pandas: operadores por elemento
velocidad > 0.1          # Series de booleanos
(vel > 0.1) & (dir < 90) # AND elemento a elemento
```

## Conversión de tipos

```python
int("23")        # 23
float("3.5")     # 3.5
str(186)         # "186"
list((1, 2, 3))  # [1, 2, 3]
```

!!! warning "Error frecuente"
    En Python 3, dividir dos enteros siempre devuelve float: `7 / 2 = 3.5`. Para división entera usa `//`.
