fruits = ['Mango', 'Pitahaya', 'Fresa', 'Manzana', 'Guayaba', 'Uva', 'Kiwi']

for fruit in fruits:
    print(f'Tenemos {fruit}s.')

for n in range(0,25): # 25 es exclusivo del range, no lo incluye
    print(n)

# Enumerar listas
for index, fruit in enumerate(fruits):
    print(f'Tenemos {fruit}s con indice {index}')

for fruit in fruits:
    if fruit != "Guayaba":
        print('I am looking for Guayaba, next')
        continue # Salta a la siguiente iteracion
    else:
        print(f'Gotcha {fruit}, breaking loop...')
        break; # Rompe la iteracion