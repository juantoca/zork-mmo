from Server.Objects.Entity import Entity


class Container(Entity):

    def __init__(self, identifier, identity_type, upper_object=None, closed=True):
        super().__init__(identifier, identity_type, upper_object)
        self.set_atribute("closed", closed)

    def get_entities(self):
        if self.get_atribute("closed"):
            return []
        return super().get_entities()

    def evento(self, event_object):
        super().evento(event_object)
        self.event_handler(event_object)

    def close(self):
        self.set_atribute("closed", True)

    def open(self):
        self.set_atribute("closed", False)

    def insert(self, objeto):
        objeto.upper_object.remove_entity(objeto)
        self.add_entity(objeto)
        print(self.entities)

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

    def evento_meter(self, evento):
        if evento.get_atribute("target") == self:
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
