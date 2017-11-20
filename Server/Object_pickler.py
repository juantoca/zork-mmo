from pickle import dumps, loads

"""
Es probable que este archivo se pudiera incluir en otra parte pero a lo mejor en el futuro quiero cambiar
el sistema de guardado(El pickle ocupa bastante espacio)
"""


def guardar(objeto):
    return dumps(objeto)


def cargar(objeto):
    return loads(objeto)
