from Server.Objects.Evento import Evento
from Server.Objects.Sala import Sala


def parse(user, command):
    """
    Parsea un comando
    :param user: Usuario
    :param command: Comando a parsear
    :return: Se ha conseguido ejecutar?
    """
    commands = {"get_description": get_descripcion,
                "get_commands": ayuda,
                "move_to": mover}

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


def get_descripcion(user, command, evento, get_evento=False):
    """
    Obtiene la descripción de un objeto
    """
    if get_evento:
        if len(command) == 0 or command[0] == "":
            return Evento("get_description", user, {"target": user.sala})
        if len(command) == 1:
            command.append(0)
        target = user.sala.query_user(command[0])
        if not target:
            target = user.target(command[0], command[1])
        if type(target) == str:
            return target
        return Evento("get_description", user, {"target": target})

    target = evento.get_atribute("target")
    if hasattr(target, "get_description"):
        if type(target) != Sala:
            user.send(target.get_description())
        else:
            user.send(target.get_description())
            entidades = [x.identifier for x in user.sala.get_entities()]
            user.send("ENTITY_LIST", formato=(user.lista(entidades, void="ANY_FEM"),))
    else:
        user.send("NO_DESCRIPTION")


def ayuda(user, command, evento, get_evento=False):
    """
    Obtiene la ayuda
    """
    if get_evento:
        return Evento("get_help", user)

    user.send("command_list")


def mover(user, command, evento, get_evento=False):
    """
    Mueve a un jugador a otra sala
    """
    if get_evento:
        if len(command) == 0:
            return Evento("get_directions", user)
        target = user.sala.direction_coords(user.translate(command[0]))
        if target:
            return Evento("move", user, {"target": target})
        return "INVALID_DIRECTION"

    if evento.identifier == "get_directions":
        user.send("DIRECTIONS", (user.lista(user.sala.get_directions(), void="ANY_FEM"),))
    else:
        user.game.move_user(user, evento.get_atribute("target"))


def set_language(user, command, evento, get_evento=False):
    """
    Cambia el idioma del jugador
    """
    if get_evento:
        if len(command) == 0:
            return Evento("get_languages", user)
        target = user.game.languages.get_languages()
        if command[0] in target:
            return Evento("set_language", user, {"target": command[0]})
        return "UNKNOWN_LANGUAGE"

    if evento.identifier == "get_languages":
        lista = user.game.languages.get_languages()
        for x in range(0, len(lista)):
            lista[x] = "·" + lista[x]
        user.send("AVAILABLE_LANGUAGES", (user.lista(lista), ))
