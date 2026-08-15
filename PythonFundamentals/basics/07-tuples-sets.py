countries = ('Spain', 'Dominican Republic', 'Andorra', 'Switzerland')
# Chequea el numero de ocurrencias de un items, coincidencia exacta
print(countries.count('Spain')) 

countries_set = set(countries)
countries_set.add('Ireland') # Agregar a un set (si no existe)
countries_set.add('Haiti')
print(countries_set)
# Remover un item de un set (si existe), no usar .remove()
countries_set.discard('Haiti')
print(countries_set)

countries1 = {'USA', 'Mexico', 'Dominican Republic', 'Spain', 'France', 'Andorra'}
countries2 = {'Mexico', 'Spain', 'Italy', 'Andorra', 'Germany', 'Switzerland'}

# Unir todos los elementos de ambos set en uno solo
print(f"Union (|): {countries1 | countries2}")
print(f"Union (.union): {countries1.union(countries2)}")

# Elementos en ambos sets
print(f"Interseccion (&): {countries1 & countries2}")
print(f"Interseccion (.intersection): {countries1.intersection(countries2)}")

# Elementos en el primero set pero no en el segundo
print(f"Diferencia (-): {countries1 - countries2}")
print(f"Diferencia (.difference): {countries1.difference(countries2)}")

# Opuesto a interseccion: Crea un set con todos los elementos que no estan en ambos sets
print(f"Symmetric difference: {countries1.symmetric_difference(countries2)}")

countries3 = {"Spain", "Mexico", 'South Africa'}
# False, ya que 'South Africa' no esta en countries1, de lo contrario, seria True
print(f"Countries 3 is subset of Countries 1: {countries3.issubset(countries1)}")
# False, ya que 'South Africa' no esta en countries1, de lo contrario, seria True
print(f"Countries 1 is superset of Countries 3: {countries1.issuperset(countries3)}")