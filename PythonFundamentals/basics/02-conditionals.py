on = True
spain = True

if on and spain:
    print("Lights are ON in SPAIN")
elif on and not spain:
    print("Lights are OFF in the third world")
else:
    print("Lights are OFF")

life = "Happy" if spain else "Mediocre"

print(f"Your life is {life}")
print("Happy" if spain else "Mediocre")

# Truthy
bool(True)
bool(1)
bool(-1) # Cualquier valor numerico diferente de 0
bool("Frase") # Cualquier string con contenido
bool(1.1)
bool(123) 
bool([1,2,3]) # Cualquier coleccion con contenido
bool((1,2,3))
bool({1,2,3})
bool(1j) # Numero imaginario

#Falsy
bool(False)
bool(0) # Cualquier valor numerico equivalente a 0
bool(0.0)
bool([]) # Cualquier coleccion vacia
bool(())
bool({})
bool("") # Cualquier string vacio
bool(None) # None = Null de otros lenguajes como C# o Typescript

print(True and True) # True
print(True and False) # False
print(False and True) # False
print(False and False) # False

print(True or True) # True
print(True or False) # True
print(False or True) # True
print(False and False) # False

print(not True) # False
print(not False) # True

print(2 + 2 == 4) # True
print(5 < 1) # False
print(3 > 2) # True
print(4 <= 4) #True
print(5 >= 6) # False
print(1 != 2) # True