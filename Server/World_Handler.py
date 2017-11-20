from peewee import *

from Server.Object_pickler import cargar, guardar

db = SqliteDatabase("Salas.db")


class Sala(Model):
    """
    Modelo de la tabla Sala
    """
    x = FloatField(primary_key=False)  # Uso floats porque es posible que para organizar
    # las salas en zonas vengan bien los decimales
    y = FloatField(primary_key=False)
    z = FloatField(primary_key=False)
    nombre = CharField()
    objeto = BareField()

    class Meta:
        database = db


if len(db.get_tables()) == 0:
    db.create_table(Sala)


def get_sala_object(coords):
    """
    Obtiene la sala de las coordenadas dadas
    :param coords: Coordenadas de la sala
    :return: Objeto Sala
    """
    try:
        return cargar(Sala.select().where((Sala.x == coords[0]) & (Sala.y == coords[1]) & (Sala.z == coords[2])).get().
                      objeto)
        # No me deja convertir las coordenadas en una tupla para compararlas asi que he tenido que hacerlo asi
    except Sala.DoesNotExist:
        return None


def set_sala_object(coords, objeto):  # TODO Encriptar objetos en la base de datos
    """
    Sobreescribe una sala en la base de datos
    :param coords: Coordenadas de la sala
    :param objeto: Objeto sala
    :return: True si existe la sala, False si no
    """
    try:
        obj = Sala.select().where((Sala.x == coords[0]) & (Sala.y == coords[1]) & (Sala.z == coords[2])).get()
        obj.objeto = guardar(objeto)
        obj.save()
        return True
    except Sala.DoesNotExist:
        return False


def create_sala_entry(objeto):
    """
    Crea una entrada para una nueva sala
    :param objeto: Objeto sala a guardar
    """
    coords = objeto.coordenadas
    name = objeto.identifier
    sala = get_sala_object(coords)
    if sala is None:
        Sala.create(x=coords[0], y=coords[1], z=coords[2], nombre=name, objeto=guardar(objeto))
    else:
        raise ValueError("Coords " + str(coords) + " taken")
