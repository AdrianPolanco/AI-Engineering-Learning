tercer_mundo = {
    'Argentina': True,
    'Haiti': True,
    'Dominican Republic': True,
    'Cuba': True,
    'Spain': False
}

key_values_iterator = iter(tercer_mundo.items())

while(next(key_values_iterator)[1]):
    print('Claro tercermundista...')
else: # Ejecutar pieza de codigo cuando ya no se cumpla la condicion (rompe el while)
    print('No, pais en el que vale la pena vivir.')