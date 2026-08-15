# Iterables: Objetos que se pueden recorrer (lists, tuples, sets, dictionaries)

# Iterators: Objetos que ademas de poderse recorrer, recuerdan su posicion

fruits = ['Mango', 'Pitahaya', 'Fresa', 'Manzana', 'Guayaba', 'Uva', 'Kiwi']

fruits_iterator = iter(fruits)

# Invocamos un item a la vez, en cada llamada con next()
print(f"Llamada 1: {next(fruits_iterator)}")
print('Hacer otra cosa....')
print(f'Ahora invocare la otra fruta: {next(fruits_iterator)}')