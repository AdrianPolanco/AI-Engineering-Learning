
print("Carrito de compras")
print("Opciones: ")
print("1. Agregar producto")
print("2. Eliminar producto")
print("3. Mostrar la lista ordenada")
print("4. Buscar producto")
print("5. Contar productos del carrito")
print("6. Vaciar el carrito")

shopping_cart = ["Laptop", "Vaso", "Cafe", "Audifonos"]
option = input("Elige una opción (1-6): ")
def add_product():
    product = input("Ingresa el producto: ")
    if product not in shopping_cart:
        shopping_cart.append(product)
    else:
        print(f"Producto no agregado: {product} ya existe en el carrito de compras.")

    return shopping_cart

def remove_product():
    product = input("Ingresa el nombre del producto a remover: ")
    if product in shopping_cart:
        shopping_cart.remove(product)
    else:
        print(f"Producto no encontrado: {product}")

    return shopping_cart

def show_sorted_list():
    return sorted(shopping_cart)

def search_product():
    product = input(f"Inserte el nombre del producto a buscar: ")
    exists = product in shopping_cart

    if exists:
        return next((item for item in shopping_cart if item.lower() == product.lower()), None)
    else:
        return next((item for item in shopping_cart if product.lower() in item.lower()),None)

def count_products():
    return len(shopping_cart)

def empty_cart():
    shopping_cart.clear()
    return shopping_cart

options = {
    "1": add_product,
    "2": remove_product,
    "3": show_sorted_list,
    "4": search_product,
    "5": count_products,
    "6": empty_cart
}

print(options[option]())
