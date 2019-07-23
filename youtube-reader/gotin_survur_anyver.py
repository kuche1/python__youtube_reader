

import os




name_prefix = 'gotin_survur_'
name_postfix = '.py'


ver = 0

while 1:
    name = f'{name_prefix}{ver}{name_postfix}'
    print(f'Searching for: {name}')
    if os.path.isfile(name):
        break
    ver += 1

print(f'Using: {name}')

__import__(name)
