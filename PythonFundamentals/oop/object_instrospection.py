"""Podemos hacer object introspection en Python, es decir, 
podemos inspeccionar los objetos en tiempo de ejecucion para obtener 
informacion sobre ellos, como sus atributos, metodos, etc. 

Esto es posible gracias a que en Python todo es un objeto, 
incluso las clases y los tipos de datos primitivos.

Similar a la reflexion en C# y Java"""




x = [1,2,3,4,5]

print(x)
# Obtener type
print(type(x))  
print(dir(x)) # Obtener todos los atributos y metodos del objeto x
print(hasattr(x, "append")) # Verificar si el objeto x tiene el atributo append
# Obtenemos la referencia a la funcion append de la lista x
append_func = getattr(x, "append") 
append_func(6) # Llamamos a la funcion append de la lista x usando la
print(x)
# Verificar si el objeto append_func es callable (es una funcion)
print(callable(append_func)) 
# Obtener direccion de memoria del objeto x
print(id(x))
