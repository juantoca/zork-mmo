from Server.Objects.Subclases.Openable import Openable


class Container(Openable):

    def __init__(self, identifier, identity_type, upper_object=None, closed=True):
        super().__init__(identifier, identity_type, upper_object)
        self.set_atribute("closed", closed)

    def get_entities(self):
        if self.get_atribute("closed"):
            return []
        return super().get_entities()

    def insert(self, objeto):
        objeto.upper_object.remove_entity(objeto)
        self.add_entity(objeto)

    def extract(self, objeto, source):
        self.remove_entity(objeto)
        source.add_entity(objeto)

    def evento_descripcion(self, evento):
        if evento.get_atribute("target") == self:
            desc = "·"
            tmp = self.get_atribute("description")
            if tmp:
                desc += evento.source.translate(tmp)
            if self.get_atribute("closed"):
                desc += ". " + evento.source.translate("CONTAINER_CLOSED")
            else:
                desc += ". " + evento.source.translate("CONTAINER_OPEN")
                desc += "\n" + evento.source.translate("CONTAINS") \
                    .format(evento.source.lista([x.identifier for x in self.get_entities()],
                                                literal=False, void="NOTHING"))
            evento.set_atribute("description", desc)

    def evento_meter(self, evento):
        if evento.get_atribute("target") == self and evento.get_atribute("objeto") != self:
            if self.get_atribute("closed"):
                evento.forbid("CONTAINER_CLOSED_INSERT")
            evento.set_atribute("callable", self.insert)

    def event_handler(self, evento):
        funciones = {"get_description": self.evento_descripcion,
                     "open": self.evento_abrir,
                     "close": self.evento_cerrar,
                     "insert_in_container": self.evento_meter}
        if evento.identifier in funciones:
            funciones[evento.identifier](evento)
