# Esto es un comentario de una linea, el interprete de Python ignorara esta linea
"""Esto es un comentario multilinea, 
el interprete de Python ignorara estas lineas"""

# Tipos de datos
"""En Python, todos los tipos de variables son "por referencia" en el sentido de que todos
contendran una referencia que apuntara a un objeto en memoria,
sin embargo, se dividen en dos: Inmutables y mutables
"""

# Tipos de datos primitivos
""" Son los tipos de datos que vienen por defecto con el lenguaje y que son el bloque
fundamental para construir otros tipos de datos mas complejos y personalizados. Algunos
ejemplos de tipos de datos primitivos son los siguientes que mencionaremos mas abajo."""

# Inmutables
# str (string)
phrase = 'hola mundo'
phrase_2 = phrase # hola mundo
phrase = phrase.capitalize() + " capitalizado" # Hola mundo capitalizado
print(f"Phrase: {phrase} vs Phrase 2: {phrase_2}")
"""
El patron f"{variable}" se llama interpolacion de strings, te permite insertar el contenido
de  ciertos tipos de variables primitivas en un string de forma natural y concisa, 
sin necesidad de concatenar (usar el operador +). Esta tecnica se utiliza normalmente con variables de tipo
str (string), int, float, listas o dict (dictionary) ya que el interprete automaticamente
muestra su contenido.
"""
# phrase_2 no se ve afectado por los cambios de phrase ya que los strings son inmutables

# int (numeros enteros)
x = 1
y = x
x += 3
print(f"x = {x}, y = {y}")

# float (numeros decimales)
x += 3.50 # Las variables tipo int se pueden operar junto a las variables de tipo float
print(f"x = {x}, y = {y}")
"""Nuevamente, tanto los int como los float son inmutables,
la variable y no se ve afectada por los cambios en x"""

# bool
# Es un tipo de dato que solo admite dos valores posibles: True o False
# Es el tipo de dato fundamental utilizado en condicionales como if, else, else if, etc.
is_sky_red = False
is_sky_blue = is_sky_red
is_sky_red = True
is_sky_blue # False

# tuple
# Una tupla es una coleccion (similar a las listas) pero inmutable
# Ver la explicacion sobre las list (listas) mas abajo
# Una vez declarada no puede cambiar
""" En algunos tipos de colecciones (listas y tuplas) 
puedes acceder a los elementos individuales de una coleccion (ej: "manzana")
usando los indices, que empiezan por el indice 0, ej: fruits_tuple[0] hace referencia
al primer elemento de fruits_tuple que corresponde a "manzana", fruits_tuple[1] al segundo, etc."""
fruits_tuple = ("manzana", "mango", "fresa")
# fruits_tuple[0] = "tomate" # Intentamos cambiar el primer elemento de la tupla 
# Dara TypeError ya que las tuplas son inmutables 

# frozenset
# Es un set (ver la explicacion sobre los sets mas abajo) pero inmutable
# No soporta mutaciones como .add o .remove, como si lo hacen los sets
roles = frozenset({"tecnico", "analista", "encargado", "encargado"})
print(f"Frozen set: {roles}") # {"tecnico", "analista", "encargado"}

# Mutables
# list
# Una lista es una coleccion de objetos que es mutable
fruit = 'uva'
# La lista es una coleccion de objetos, las variables almacenan objetos
# Por tanto, en las listas (y cualquier tipo de coleccion) se pueden poner variables dentro de ellas
fruits = ["manzana", "mango", "fresa", fruit] 
fruits_2 = fruits
fruits.append("kiwi") # Mutacion: Agregamos "kiwi" al final de la lista
print(f"Frutas: {fruits}") # ["manzana", "mango", "fresa", "uva", "kiwi"]
print(f"Fruits 2: {fruits_2}") # ["manzana", "mango", "fresa", "uva", "kiwi"]
""" fruits_2 tambien se ve afectado por los cambios en fruits, 
ya que ambas variables hacen referencia a la misma lista, y las listas son mutables"""

# sets
""" Es una coleccion de elementos unicos (los duplicados son eliminados automaticamente),
 no ordenada (no mantiene el orden de sus elementos como lo hacen las listas y las tuplas, 
 osea, en una ejecucion "fresa" puede ser el primer elemento, 
y en la proxima puede ser el segundo o el ultimo), no indexada (no se puede acceder a los
elementos individuales usando indices como fruits_set[0])"""
fruits_set = {"manzana", "manzana", "mango", "fresa"} # {"manzana", "mango", "fresa"}
print(f"Set: {fruits_set}")
# fruits_set[1] # Esto tambien falla (TypeError), los sets no soportan el uso de indices
is_apple_in_set = "manzana" in fruits_set 
fruits_set_2 = fruits_set
fruits_set.add("pitahaya") # Modificamos el set
print(f"Set modificado: {fruits_set}") # {"manzana", "mango", "fresa", "pitahaya"}
# Ideal para busquedas rapidas como ver si X elemento pertenece a una coleccion
print(f"La manzana esta en el conjunto?: {is_apple_in_set}")
# Ideal para operaciones de conjuntos
A = {1,2,3,6}
B = {3,4,5,6,7, 7}

# Union: Devuelve un nuevo set con todos los elementos de ambos sets
print(f"AuB: {A | B}") # {1,2,3,4,5,6,7}, recuerda que los sets no admiten duplicados

# Interseccion: Devuelve un nuevo set solo los elementos que estan en ambos sets
print(f"A∩B: {A & B}") # {3,6}

#Diferencia: Devuelve un nuevo set con los elementos que estan en el primer set pero no en el segundo
print(f"A-B: {A - B}") # {1,2}

# dict (diccionarios)
""" Es una estructura de datos clave-valor, donde usando las claves puedes determinar
obtener rapida y directamente el valor asociado a ella, por eso, obtener un valor de 
un diccionario es complejidad O(1)."""

salaries_cache = {
    "tecnico": 40000,
    "analista": 70000,
    "encargado": 110000,
    "gerente": 30,
    "gerente": 250000
}
salaries_cache_2 = salaries_cache
salaries_cache_2["director"] = 350000 # Agregamos una nueva entrada al diccionario

print(f"Diccionario 1: {salaries_cache}")
""" Output: {
    "tecnico": 40000,
    "analista": 70000,
    "encargado": 110000,
    "gerente": 250000
}

salaries_cache fue modificado ya que se agrego una entrada a salaries_cache_2 y
tanto salaries_cache como salaries_cache_2 hacen referencia al mismo objeto
"""
"""Acceder a un valor de un diccionario es extremadamente rapido (O(1)) 
ya que busca por su clave, la cual es unica (si se declara varias veces la misma
clave, solo se tomara en cuenta el valor de la ultima declaracion, como ya vimos)"""
print(f"Salario del gerente: {salaries_cache['gerente']}")

"""Objetos indexables: Son objetos donde se pueden usar indices para acceder de forma
rapida a un elemento especifico. Los tipos que soportan indexacion son:

list
tuple
str (string)"""

phrase = "Hola Adrian"
print(phrase[2]) # l
"""[5:11:1] -> [start_index_inclusive:end_index_exclusive:steps (optional)]
start_index_inclusive = Posicion de inicio (inclusiva), en este caso Posicion 5 = A

end_index_exclusive = Posicion final (exclusiva, si n es posicion 10, y usaramos [5:10:1])
no incluiria n y quedaria como "Adria"

steps = Cuantos elementos se va a saltar, si usas 1, iras elemento por elemento en ese rango
sin saltarte ninguno, por tanto, en la practica [5:11:1] y [5:11] serian equivalentes. Si usas
un step superior a 1, saltara steps - 1 elementos, si por ejemplo usas 2, saltara un elemento,
por ejemplo, [5:11:2] devuelve "Ara" (AdRiAn)
"""
print(phrase[5:11:1]) # Adrian
print(phrase[5:11]) # Adrian
print(phrase[5:11:2]) # Ara

print((1,2,3)[1]) # 2

print([1,4,"hola"][2]) # "hola"
#Usar numeros negativos en el indice lo que hace es que empieces al reves
# -1 es el ultimo elemento de la coleccion, -2 el penultimo, etc.
print(phrase[-1]) # n
# Si no ponemos nada antes de :, empezara por el primer elemento, equivalente a usar [0:n]
print(phrase[:-1]) # Hola Adria (excluyendo al ultimo elemento)
print(phrase[1:]) # ola Adrian (desde el segundo elemento hasta el ultimo)
print(phrase[1::3]) # o rn (Empieza desde el segundo (1), y va de 2 en 2: "Ola adRiaN")

name = "Adrian"
print(name[::-1]) # nairdA (Nombre al reves), ya que el step tambien puede ser negativo