from Server.Objects.Entity import Entity
from Server.Objects.Commands.UserCommands import parse
from Server.Objects.Subclases.UserEntities.Inventario import Inventario


class Personaje(Entity):

    def __init__(self, nick, initial_coords, bio=""):
        super().__init__(nick)
        self.nick = nick
        self.coords = initial_coords
        self.desc = bio
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

    def lista(self, raw_lista: list, void: str = "ANY_MASC") -> str:
        """
        Devuelve una string que forma una enumeración de elementos (elemento1, elemento2 y elemento3) de una lista
        sin traducir
        :param raw_lista: Lista de tokens
        :param void: Token que usar cuando la lista esta vacía
        :return: String lista para enviar
        """
        translated_lista = []
        for x in raw_lista:
            translated_lista.append(self.translate(x))
        long = len(translated_lista)
        if long == 0:
            return "·" + self.translate(void)
        elif long == 1:
            return "·" + self.translate(translated_lista[0])
        returneo = "·"
        for x in translated_lista[:-2]:
            returneo += x + ", "
        returneo += translated_lista[-2] + " " + self.translate("AND") + " " + translated_lista[-1]
        return returneo

    def get_description(self):
        return self.desc

    def handle_command(self, command):
        command = command.split(" ")
        command[0] = self.translate(command[0])
        if not parse(self, command):
            handled = self.sala.exec_command(self, command)
            if not handled:
                self.send("INVALID_COMMAND")
