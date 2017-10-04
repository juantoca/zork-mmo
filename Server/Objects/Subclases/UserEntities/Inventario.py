from Server.Objects.Entity import Entity
from Server.Objects.Evento import Evento


class Inventario(Entity):

    def __init__(self, identifier, upper_object):
        super().__init__(identifier, upper_object)

    def coger(self, user, command, evento, get_evento=False):
        if get_evento:
            if len(command) == 0:
                return "INVALID_SINTAX"
            target = user.sala.query_entity(user.translate(command[0]))
            if target:
                return Evento("pick_object", user, {"target": target})
            return "ENTITY_NOT_FOUND"

        if type(evento) != evento:
            user.send(evento)
        else:
            self.add_entity(evento.get_atribute("target"))
            user.sala.

    def parse_command(self, user, command):
        commands = {}

        if command[0] not in commands:
            return False
        evento = user.sala.orden(commands[command[0]](user, command[1:], None, get_evento=True))
        if not evento.permited:
            user.send(evento.not_permited_txt)
        else:
            commands[command[0]](user, command[1:], evento)
        return True
