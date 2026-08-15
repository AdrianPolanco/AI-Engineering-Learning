print(0 in range(1, 10)) # False range(1,10) = [1,2,3,4,5,6,7,8,9]
print(0 not in range(1,10)) # True

brands = { "Azzaro", "Valentino", "Rabanne", "Xerjoff"}

"Valentino" not in brands # False

phrase = "Yo se Python"

print("Python" in phrase)

arr1 = []
arr2 = arr1
arr3 = []
print(arr2 == arr1) # True, ya que compara por contenido
print(arr2 is arr1) # True, ya que compara la referencia de la instancia en memoria
print(arr1 is arr3) # False, no comparten la misma instancia o referencia de la lista en memoria
print(arr1 == arr3) # True, ya que ambas listas estan vacias