"""
A variable that exists outside of the except handler is not changed.
"""

class Entity:
    def __init__(self, name):
        self.message = name

e = Entity('karl')
print(e.message)

try:
    import doesnt_exist
except ImportError as e:
    print(e.message)


e = Entity('thebe')
print(e.message)

