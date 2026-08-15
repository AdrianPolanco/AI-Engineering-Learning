person = {
    "name": "Adrian",
    "lastname": "Polanco",
    "country": "Spain",
    "age": 24
}

print(f"Age key is in dictionary: {"age" in person.keys()}")
print(f"dict.keys(): {person.keys()}") # ['name', 'lastname', 'country', 'age']
print(f"dict.values(): {person.values()}") # [ 'Adrian', 'Polanco', 'Spain', 24 ]
# [('name', 'Adrian'), ('lastname', 'Polanco'), ('country', 'Spain'), ('age', 24)]
print(f"dict.items(): {person.items()}") 
# Copiar el diccionario a una nueva referencia en memoria
person_2 = person.copy()
person_2['name'] = "Saul"

print(f"Person 1: {person} vs Person 2: {person_2}")
# Alternativa a dict[key]
print(person_2.get('age'))
# Eliminar propiedad por clave
person_2.pop('age')
print(person_2)
# Eliminar el ultimo item (key:value) sin usar la key
person_2.popitem()
print(person_2)
# Agregar item (key:value) -> Equivalente a dict['newKey'] = 'newValue'
person_2.setdefault('country', 'Spain')
person_2.setdefault('age', 24)
print(person_2)
# Actualizar item (key:value) -> Equivalente a dict['existingKey'] = 'newValue'
person_2.update({'age': 25})
print(person_2)
