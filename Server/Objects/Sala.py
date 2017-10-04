
"""
Las salas se encargan de recibir todas las acciones de todas las entidades dentro de ella, son enviadas al resto
de objetos para que modifiquen la accion y, finalmente, llaman a la funcion run del evento para que realize la
accion
"""
from Server.Objects.Evento import Evento


class Sala:

    def __init__(self, identifier, coordenadas, conexiones):

        self.identifier = identifier
        self.coordenadas = coordenadas
        self.conexiones = conexiones  # {direccion: coordenadas}
        self.usuarios = {}
        self.entidades = {}
        self.description = None

    def orden(self, evento):
        if type(evento) != Evento:
            return evento
        for x in self.usuarios.values():
            x.evento(evento)
        for x in self.entidades.values():
            x.evento(evento)
        return evento

    def add_user(self, user):
        self.usuarios[user.nick] = user

    def remove_user(self, user):
        del self.usuarios[user.nick]

    def prepare_save(self):
        entidades = list(self.entidades.values())
        for x in entidades:
            x.prepare_save()

    def update(self):
        entidades = list(self.entidades.values())
        for x in entidades:
            x.update()

    def save(self):
        self.prepare_save()
        from Server.World_Handler import set_sala_object
        dic_tmp = self.usuarios
        self.usuarios = {}
        set_sala_object(self.coordenadas, self)
        self.usuarios = dic_tmp

    def query_user(self, identifier):  # TODO Entidades ocultas
        returneo = None
        if identifier in self.usuarios:
            return self.usuarios[identifier]
        return returneo

    def query_entity(self, identifier):
        returneo = None
        if identifier in self.entidades:
            return self.entidades[identifier]
        for x in self.usuarios.values():
            query = x.query_entity(identifier)
            if query is not None:
                return query
        for x in self.entidades.values():
            returneo = x.query_entity(identifier)
        return returneo

    def add_entity(self, entity, force=False):
        if entity.identifier not in self.entidades or force:
            self.entidades[entity.identifier] = entity
        else:
            raise KeyError("Se ha intentado sobreescribir una entidad")

    def get_users(self):
        jugadores = []
        for x in self.usuarios.keys():
            jugadores.append("·"+x)
        return jugadores

    def get_entities(self):  # TODO Entidades ocultas
        return list(self.entidades.keys())

    def parse_command(self, user, command):  # TODO Comandos de la sala
        pass

    def exec_command(self, user, command):
        if self.parse_command(user, command):
            return True
        for x in self.entidades.values():
            if x.exec_command(user, command):
                return True
        for x in self.usuarios.values():
            if x.exec_command(user, command):
                return True
        return False

    def get_description(self):
        return self.description

    def direction_coords(self, direction):
        if direction in self.conexiones:
            return self.conexiones[direction]
        else:
            return None

    def get_directions(self):
        return list(self.conexiones.keys())
