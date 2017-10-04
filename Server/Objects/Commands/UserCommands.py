from Server.Objects.Evento import Evento


def parse(user, command):
    commands = {"get_description": get_descripcion,
                "get_commands": ayuda,
                "move_to": mover}

    if command[0] not in commands:
        return False
    evento = user.sala.orden(commands[command[0]](user, command[1:], None, get_evento=True))
    if not evento.permited:
        user.send(evento.not_permited_txt)
    else:
        commands[command[0]](user, command[1:], evento)
    return True


def get_descripcion(user, command, evento, get_evento=False):
    if get_evento:
        if len(command) == 0 or command[0] == "":
            return Evento("get_description", user, {"target": user.sala})
        target = user.sala.query_user(command[0])
        if not target:
            target = user.sala.query_entity(user.translate(command[0], warn=False))
        if target:
            return Evento("get_description", user, {"target": target})
        return "ENTITY_NOT_FOUND"

    if type(evento) != Evento:
        user.send(evento)
        return
    target = evento.get_atribute("target")
    if hasattr(target, "get_description"):
        user.send(target.get_description())
        user.send("ENTITY_LIST", formato=(user.lista(user.sala.get_entities()),))
    else:
        user.send("NO_DESCRIPTION")


def ayuda(user, command, evento, get_evento=False):
    if get_evento:
        return Evento("get_help", user)

    user.send("command_list")


def mover(user, command, evento, get_evento=False):
    if get_evento:
        if len(command) == 0:
            return Evento("get_directions", user)
        target = user.sala.direction_coords(user.translate(command[0]))
        if target:
            return Evento("move", user, {"target": target})
        return "INVALID_DIRECTION"

    if type(evento) != Evento:
        user.send(evento)
        return
    if evento.identifier == "get_directions":
        user.send("DIRECCIONES", (user.lista(user.sala.get_directions(), void="ANY_FEM"),))
    else:
        user.game.move_user(user, evento.get_atribute("target"))


def set_language(user, command, evento, get_evento=False):
    if get_evento:
        if len(command) == 0:
            return Evento("get_languages", user)
        target = user.game.languages.get_languages()
        if command[0] in target:
            return Evento("set_language", user, {"target": command[0]})
        return "UNKNOWN_LANGUAGE"

    if type(evento) != Evento:
        user.send(evento)
        return
    if evento.identifier == "get_languages":
        lista = user.game.languages.get_languages()
        for x in range(0, len(lista)):
            lista[x] = "·" + lista[x]
        user.send("AVAILABLE_LANGUAGES", (user.lista(lista), ))
