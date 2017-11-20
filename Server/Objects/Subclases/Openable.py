from Server.Objects.Entity import Entity


class Openable(Entity):

    def __init__(self, identifier, identity_type, upper_object, closed=True):
        super().__init__(identifier, identity_type, upper_object)
        self.set_atribute("closed", closed)

    def close(self):
        self.set_atribute("closed", True)

    def open(self):
        self.set_atribute("closed", False)

    def evento_abrir(self, evento):
        if evento.get_atribute("target") == self:
            if not self.get_atribute("closed"):
                evento.forbid("ALREADY_OPEN")
            evento.set_atribute("callable", self.open)

    def evento_cerrar(self, evento):
        if evento.get_atribute("target") == self:
            if self.get_atribute("closed"):
                evento.forbid("ALREADY_CLOSED")
            evento.set_atribute("callable", self.close)

    def evento_descripcion(self, evento):
        dic = {True: "OPENABLE_CLOSED", False: "OPENABLE_OPEN"}
        desc = "·" + evento.source.translate(self.get_atribute("description")) \
               + evento.source.translate(dic[self.get_atribute("closed")])
        if evento.get_atribute("target") == self and desc:
            evento.set_atribute("description", desc)
