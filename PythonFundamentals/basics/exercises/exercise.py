""" Soy un vendedor de frutas, que quiero reabastecer mi inventario, pero no quiero
comprar frutas, que ya tengo, solo frutas que se me hayan acabado"""

Lista_Yari = ['Tomate', 'Aguacate', 'Aguacate', 'Naranja', 'Banana', 'Piña', "Lechosa"]
Lista_Yari.append("Fresa")
Lista_Yari.append("Tomate")
Lista_Yari.append("Naranja")
print(Lista_Yari)

#Lista_Yari.remove("Tomate")
#Lista_Yari.remove("Naranja")
#Lista_Yari.remove("Aguacate")
#print("Lista deduplicada ", Lista_Yari)

fruits_set = set(Lista_Yari)
print(f"Lista deduplicada: {fruits_set}")