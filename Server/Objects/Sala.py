
"""
Las salas se encargan de recibir todas las acciones de todas las entidades dentro de ella, son enviadas al resto
de objetos para que modifiquen la accion y, finalmente, llaman a la funcion run del evento para que realize la
accion
"""
from Server.Objects.Evento import Evento
from Server.Objects.Entity import Entity


def descripcion(sala, evento):
    desc = "·"
    tmp = sala.get_atribute("description")
    if tmp:
        desc += evento.source.translate(tmp)
    desc += "\n"+evento.source.translate("ENTITY_LIST")\
        .format(evento.source.lista([x.identifier for x in sala.get_entities()], literal=False))
    evento.set_atribute("description", desc)


def event_handler(sala, evento):
    funciones = {"get_description": descripcion}
    if evento.identifier in funciones:
        funciones[evento.identifier](sala, evento)


class Sala(Entity):

    def __init__(self, identifier, coordenadas, conexiones):
        super().__init__(identifier, "ROOM")
        self.coordenadas = coordenadas
        self.conexiones = conexiones  # {direccion: coordenadas}
        self.usuarios = {}
        self.upper_object = None

    def orden(self, evento):
        """
        Activa los protocolos de las entidades para los eventos
        :param evento: Evento que checkear
        :return: Evento recibido
        """
        if type(evento) != Evento:
            return evento
        if evento.get_atribute("target") == self:
            event_handler(self, evento)
        for x in self.usuarios.values():
            x.evento(evento)
        for x in self:
            x.evento(evento)
        return evento

    def add_user(self, user):
        """
        Añade un usuario a la sala
        :param user: Usuario a añadir
        """
        self.usuarios[user.nick] = user

    def remove_user(self, user):
        """
        Borra un usuario de la sala
        :param user: Usuario a borrar
        """
        del self.usuarios[user.nick]

    def save(self):
        """
        Vuelca la sala a la base de datos
        """
        from Server.World_Handler import set_sala_object
        dic_tmp = self.usuarios
        self.usuarios = {}
        self.prepare_save()
        set_sala_object(self.coordenadas, self)
        self.usuarios = dic_tmp

    def query_user(self, identifier):
        """
        Devuelve el usuario con el nick especificado
        :param identifier: Nick del usuario
        """
        returneo = None
        if identifier in self.usuarios:
            return self.usuarios[identifier]
        return returneo

    def query_entity(self, identifier):
        """
        Devuelve las entidades que responden al identificador especificado
        :param identifier: Identificador de las entidades
        :return: [Entity]
        """
        returneo = super().query_entity(identifier)
        for x in self.usuarios.values():
            returneo += x.query_entity(identifier)
        return returneo

    def search_type(self, type_identifier):
        """
        Devuelve las entidades del tipo especificado
        :param type_identifier: Tipo de las entidades
        :return: [Entity]
        """
        returneo = super().search_type(type_identifier)
        for x in self.usuarios.values():
            returneo += x.search_type(type_identifier)
        return returneo

    def get_users(self):
        """
        Devuelve la lista de usuarios
        :return: [User]
        """
        jugadores = []
        for x in self.usuarios.keys():
            jugadores.append("·"+x)
        return jugadores

    def exec_command(self, user, command):
        """
        Ejecuta el comando especificado
        :param user: Usuario que ejecuta el comando
        :param command: Comando a ejecutar
        :return: Se ha conseguido ejecutar?
        """
        if self.parse_command(user, command):
            return True
        for x in self:
            if x.exec_command(user, command):
                return True
        for x in self.usuarios.values():
            if x.exec_command(user, command):
                return True
        return False

    def direction_coords(self, direction):
        """
        Obtiene las coordenadas de la dirección especificada
        :param direction: Dirección a buscar
        :return: None si la direccion no existe o coordenadas si existe
        """
        if direction in self.conexiones:
            return self.conexiones[direction]
        else:
            return None

    def get_directions(self):
        return list(self.conexiones.keys())

    def load(self, game):
        self.set_game(game)

    def send_all(self, msg, formato=(), excepto=()):
        """
        Manda a todos los usuarios un mensaje
        :param msg: Mensaje a mandar
        :param formato: .format()
        :param excepto: lista de nicks a excluir a excluir
        """
        for x in self.usuarios.values():
            if x.nick not in excepto:
                x.send(msg, formato)
