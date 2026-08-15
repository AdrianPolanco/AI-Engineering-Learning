numbers = [1,2,2,3,3,3,4,5,6,6,6,7,7,7,8,9,9,10]

numbers_tuple = tuple(numbers)

numbers_list = list(numbers_tuple)

numbers_set = set(numbers)

numbers_frozen_set = frozenset(numbers)

numbers_to_dictionary  = [('a',1), ('b',2), ('c', 3), ('d', 4)]

numbers_dict = dict(numbers_to_dictionary)

print(f'List: {numbers_list}')
print(f'Tuple: {numbers_tuple}')
print(f'Set: {numbers_set}')
print(f'Frozen set: {numbers_frozen_set}')
print(f'Dictionary: {numbers_dict}')