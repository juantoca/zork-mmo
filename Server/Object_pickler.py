from pickle import dumps, loads


def guardar(objeto):
    return dumps(objeto)


def cargar(objeto):
    return loads(objeto)
