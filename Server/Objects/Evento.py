

class Evento:

    def __init__(self, identifier: str, source, atributes: dict={}):
        self.identifier = identifier
        self.source = source
        self.permited = True
        self.not_permited_txt = ""
        self.atributes = atributes

    def get_atribute(self, atribute: str):
        if atribute in self.atributes:
            return self.atributes[atribute]
        else:
            return None

    def set_atribute(self, atribute: str, valor):
        if atribute in self.atributes:
            self.atributes[atribute] = valor
        else:
            raise KeyError("El atributo modificado no esta contemplado para este evento")

    def forbid(self, message):
        self.permited = False
        self.not_permited_txt = message
