
"""
Las salas se encargan de recibir todas las acciones de todas las entidades dentro de ella, son enviadas al resto
de objetos para que modifiquen la accion y, finalmente, llaman a la funcion run del evento para que realize la
accion
"""
from Server.Objects.Evento import Evento
from Server.Objects.Entity import Entity


class Sala(Entity):

    def __init__(self, identifier, coordenadas, conexiones):
        super().__init__(identifier)
        self.coordenadas = coordenadas
        self.conexiones = conexiones  # {direccion: coordenadas}
        self.usuarios = {}
        self.description = None

    def orden(self, evento):
        if type(evento) != Evento:
            return evento
        for x in self.usuarios.values():
            x.evento(evento)
        for x in self.entities.values():
            x.evento(evento)
        return evento

    def add_user(self, user):
        self.usuarios[user.nick] = user

    def remove_user(self, user):
        del self.usuarios[user.nick]

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
        if identifier in self.entities:
            return self.entities[identifier]
        for x in self.usuarios.values():
            query = x.query_entity(identifier)
            if query is not None:
                return query
        for x in self.entities.values():
            returneo = x.query_entity(identifier)
            if returneo:
                return returneo
        return None

    def get_users(self):
        jugadores = []
        for x in self.usuarios.keys():
            jugadores.append("·"+x)
        return jugadores

    def get_entities(self):  # TODO Entidades ocultas
        return list(self.entities.keys())

    def exec_command(self, user, command):
        if self.parse_command(user, command):
            return True
        for x in self.entities.values():
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
