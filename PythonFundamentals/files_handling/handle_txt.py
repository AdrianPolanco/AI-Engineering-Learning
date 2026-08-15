# txt = open("file.txt", "r")

# Con with el archivo se cierra automaticamente al terminar el bloque de codigo
# Liberando recursos y evitando errores de memoria
with open("file.txt", "r") as txt:
    content = txt.read()
    print(content)

# r+ permite leer y escribir en el archivo, pero no permite crear un archivo nuevo
with open("file.txt", "r+") as txt:
    content = txt.read()
    print(content)
    txt.write("\nNew line added to the file.")

# w permite escribir en el archivo, pero no permite leerlo y si el archivo ya existe, se sobreescribe
with open("file.txt", "w") as txt:
    txt.write("This will overwrite the existing content of the file.")

# a permite agregar contenido al final del archivo, pero no permite leerlo
with open("file.txt", "a") as txt:
    txt.write("\nThis line will be appended to the file.")