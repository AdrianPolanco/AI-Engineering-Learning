# Son colecciones mutables, indexables y que admiten duplicados

divisas = [ "dolares", "euros", "yenes", "rupias", "pesos", "pesos"]

# Agregar al final
divisas.append("libra esterlina")
# Insertar en la posicion 2 y desplazar la actual ("yenes") a la posicion 3
divisas.insert(2, "pesetas")
print(divisas)
# Insertar los elementos de un array en otro y aplanarlos
divisas.extend(["francos", "wons", "dolares canadienses", "gourdes"])
print(f"Divisas extendida: {divisas}")
# Eliminar ultimo elemento de la lista
divisas.pop()
# Encontrar el index de un valor
print(divisas.index("euros"))
#Encontrar el index de un valor entre 1 y 4 (4 exclusivo)
print(divisas.index("euros", 1, 4))
# Saber cuantas veces esta un elemento en una list
print(divisas.count("pesos"))
# Chequear si un elemento esta en una list
print("euros" in divisas)
# Ordernar la list
divisas.sort()
# Ordernar la list (sin alterar la original) y copiarla en una nueva list
divisas2 = sorted(divisas)
# Copiar la list
divisas3 = divisas[:]
divisas4 = divisas.copy()
#Reversar la lista (altera la lista original)
divisas.reverse()
# Reversar la lista (copiandola, no altera la lista original)
divisas5 = divisas[::-1]
divisas.append("Yenes japoneses")
print(f"Normal: {divisas} vs Reversed: {divisas5}")
# Crear una lista del 0 al 100 (no incluye al 101)
hundred = list(range(101))
print(hundred)
phrase = ' '.join(["Te", "amo", "mas", "que", "a", "un", "nuevo", "dia"])
print(phrase) #Genera un string separado por el string antes de .join()

numbers = [101, -3, 4, -1500, 85, 345, 284, 895, 376, 404, 506, 4488, 394]

print(max(numbers)) # Valor mas alto
print(min(numbers)) # Valor mas bajo
print(sum(numbers)) # Suma de todos los valores

yenes, wons, rupias, *partial_currencies, yenes_japoneses = divisas

print(yenes)
print(partial_currencies)
print(yenes_japoneses)