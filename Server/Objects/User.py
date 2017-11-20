from Server.Objects.Entity import Entity
from Server.Objects.Commands.UserCommands import parse
from Server.Objects.Subclases.UserEntities.Inventario import Inventario


class Personaje(Entity):

    def __init__(self, nick, initial_coords):
        super().__init__(nick, "USER")
        self.nick = nick
        self.coords = initial_coords
        self.cache = {}  # Zona donde las entidades pueden almacenar informacion(progreso de misión, etc...)
        self.language = "español"
        self.sala = None
        self.game = None
        self.conn = None
        self.add_entity(Inventario("INVENTORY"))

    def save(self):
        """
        Vuelca el usuario a la base de datos
        """
        self.prepare_save()
        from Server.Login import set_user_object
        permanencia = [self.sala, self.game, self.conn]
        self.sala = None
        self.game = None
        self.conn = None
        set_user_object(self.nick, self)
        self.sala, self.game, self.conn = permanencia

    def translate(self, token: str, warn: bool=True) -> str:
        """
        Traduce un token dado
        :param token: Token a traducir
        :param warn: Debo advertir si no se ha concedido traducir?
        :return: Traducción del token
        """
        if token == "":
            return ""
        elif token[0] == "·":
            return token[1:]
        else:
            return self.game.languages.get_option(token, self.language, warn)

    def send(self, token: str, formato: (tuple, list)=()):
        """
        Manda un token dado, traduciendole y aplicandole format
        :param token: Token a enviar
        :param formato: Lista de campos que usar en la función format
        """
        forma = []
        for x in formato:
            forma.append(self.translate(x))
        self.conn.send(self.translate(token).format(*forma))

    def get_raw(self, token: str, formato: (tuple, list)=()):
        """
        Obtiene el valor de un token con un "·" listo para pasar por pantalla
        :param token: Token a traducir
        :param formato: Lista para usar .format()
        :return: String traducida
        """
        return "·"+self.translate(token).format(*[self.translate(x) for x in formato])

    def lista(self, raw_lista: list, void: str = "ANY_MASC", natural_language=True
              , literal=True) -> str:
        """
        Devuelve una string que forma una enumeración de elementos (elemento1, elemento2 y elemento3) de una lista
        sin traducir
        :param raw_lista: Lista de tokens
        :param void: Token que usar cuando la lista esta vacía
        :param natural_language: Debo enumerar con comas e "y"s o como listas de la compra?
        :param literal: Debo devolverlo con un "·" delante para que las funciones de traducción lo tomen como literal?
        :return: String lista para enviar
        """
        initial = ""
        if literal:
            initial = "·"
        translated_lista = []
        for x in raw_lista:
            translated_lista.append(self.translate(x))
        long = len(translated_lista)
        if long == 0:
            return initial + self.translate(void)
        returneo = initial
        if natural_language:
            if long == 1:
                return initial + translated_lista[0]
            for x in translated_lista[:-2]:
                returneo += x + ", "
            returneo += translated_lista[-2] + " " + self.translate("AND") + " " + translated_lista[-1]
        else:
            for x in translated_lista:
                returneo += "\n- " + x
        return returneo

    def handle_command(self, command):
        """
        Protocolo de ejecución de un comando
        :param command: Comando a parsear
        """
        if command == "":
            return
        command = command.split(" ")
        try:
            command.remove("")
        except ValueError:
            pass
        command[0] = self.translate(command[0])
        if not parse(self, command):
            handled = self.sala.exec_command(self, command)
            if not handled:
                self.send("INVALID_COMMAND")

    def target(self, type_identifier, ind=0, source=None):
        """
        Protocolo de seleccion de entidades objetivo
        :param type_identifier: Tipo de entidad a buscar
        :param ind: Numero de entidad a seleccionar
        :param source: Objeto en el que buscar
        :return: String si no se ha seleccionado una entidad o Entidad si se ha seleccionado
        """
        try:
            ind = int(ind)
        except:
            return "FORBIDDEN_INDEX"
        if source is None:
            source = self.sala
        possibilities = source.search_type(type_identifier)
        if len(possibilities) == 0:
            return "ENTITY_NOT_FOUND"
        elif len(possibilities) == 1:
            return possibilities[0]
        else:
            if not ind:
                returneo = "·" + self.translate("TOO_MANY_ENTITIES")
                for x in range(0, len(possibilities)):
                    entity = possibilities[x]
                    returneo += "\n" + str(x+1) + ". " + self.translate(entity.identifier)
                return returneo
            else:
                if ind > len(possibilities):
                    return "FORBIDDEN_INDEX"
                else:
                    return possibilities[ind-1]
