# Argumentos por defecto usando param=default
def greet(greeting: str = 'Hello', name: str =' Someone') -> str:
    return f'{greeting}, {name}'

tax_global = 0.18

def change_tax():
    tax_global = 1

def change_global_tax(n: float) -> None:
    global tax_global
    tax_global = n

print(tax_global)
change_tax()
# No cambia el valor del tax_global ya que el que esta dentro de la funcion
# es otra variable diferente dentro del scope de la function
print(tax_global) 

change_global_tax(2)
# Si cambia ya que en change_global_tax se accedio al tax_global en el scope global
print(tax_global)

def outer():
    outer_variable = 7

    def inner():
        # Indica a la funcion que debe buscar la variable fuera del scope local
        nonlocal outer_variable
        outer_variable = 3

    print(outer_variable)
    print('Calling inner function...')
    inner()

    return inner

outer()

# *args = Tupla
def undetermined_function(*args): # Numero de argumentos indeterminado
    print(args)

undetermined_function("Hola", 1 ,2,3, True)

# *kwargs = Diccionario
def undetermined_function_dict(*args, **kwargs):
    print(args)
    print(kwargs)

undetermined_function_dict(1,2,3, name='Adrian', age = 24, country = 'Spain')