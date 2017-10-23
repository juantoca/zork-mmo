from Server.Objects.Entity import Entity
from Server.Objects.Evento import Evento


class Inventario(Entity):

    def __init__(self, identifier):
        super().__init__(identifier, "INVENTORY")

    def coger(self, user, command, evento, get_evento=False):  # TODO Sistema de pesos
        """
        Recoge un objeto de la sala
        """
        if get_evento:
            if len(command) == 0:
                return "INVALID_SINTAX"
            if len(command) == 1:
                command.append(0)
            target = user.target(command[0], command[1])
            if type(target) != str:
                if not target.get_atribute("pickable"):
                    return "NOT_PICKABLE"
                return Evento("pick_object", user, {"target": target})
            return target

        target = evento.get_atribute("target")
        self.add_entity(target, set_upper=False)
        target.get_upper_object().remove_entity(target)
        target.set_upper_object(self)

    def drop(self, user, command, evento, get_evento=False):
        """
        Suelta un objeto a la sala
        """
        if get_evento:
            if len(command) == 0:
                return "INVALID_SINTAX"
            if len(command) == 1:
                command.append(0)
            target = user.target(command[0], command[1], self)
            if type(target) != str:
                if target.get_atribute("not_dropable"):
                    return "NOT_DROPABLE"
                return Evento("drop_object", user, {"target": target})
            if target == "ENTITY_NOT_FOUND":
                target = "ENTITY_NOT_IN_INVENTORY"
            return target

        target = evento.get_atribute("target")
        user.sala.add_entity(target, set_upper=False)
        target.set_upper_object(user.sala)
        self.remove_entity(target)
        target.set_atribute("pickable", True)

    def inventory(self, user, command, evento, get_evento=False):
        """
        Muestra la información del inventario
        """
        if get_evento:
            return Evento("get_inventory_info", user)

        lista = [x.identifier for x in self.entities]
        lista_translated = user.lista(lista, "ANY_MASC", natural_language=False)
        user.send("INVENTORY_CONTENTS", (lista_translated, ))

    def parse_command(self, user, command):
        commands = {"pick": self.coger,
                    "drop": self.drop,
                    "query_inventory": self.inventory}

        if command[0] not in commands:
            return False
        evento = user.sala.orden(commands[command[0]](user, command[1:], None, get_evento=True))
        if type(evento) == str:
            user.send(evento)
        elif type(evento) == Evento and not evento.permited:
            user.send(evento.not_permited_txt)
        else:
            commands[command[0]](user, command[1:], evento)
        return True
