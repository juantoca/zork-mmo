from Server.Objects.Entity import Entity
from Server.Objects.Evento import Evento


class Inventario(Entity):

    def __init__(self, identifier):
        super().__init__(identifier)

    def coger(self, user, command, evento, get_evento=False):  # TODO Sistema de pesos
        """
        Recoge un objeto de la sala
        """
        if get_evento:
            if len(command) == 0:
                return "INVALID_SINTAX"
            target = user.sala.query_entity(user.translate(command[0]))
            if target:
                if not target.get_atribute("pickable"):
                    return "NOT_PICKABLE"
                if target.identifier in self.entities:
                    return "ALREADY_PICKED"
                return Evento("pick_object", user, {"target": target})
            return "ENTITY_NOT_FOUND"

        if type(evento) != Evento:
            user.send(evento)
        else:
            target = evento.get_atribute("target")
            self.add_entity(target, set_upper=False)
            if not target.get_atribute("infinite"):
                target.get_upper_object().remove_entity(target)
            target.set_upper_object(self)

    def parse_command(self, user, command):
        commands = {"pick": self.coger}

        if command[0] not in commands:
            return False
        evento = user.sala.orden(commands[command[0]](user, command[1:], None, get_evento=True))
        if type(evento) == Evento and not evento.permited:
            user.send(evento.not_permited_txt)
        else:
            commands[command[0]](user, command[1:], evento)
        return True
