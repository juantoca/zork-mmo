from Server.Objects.Subclases.Openable import Openable


class Door(Openable):

    def __init__(self, identifier, identity_type, upper_object=None, coords=(), closed=True):
        super().__init__(identifier, identity_type, upper_object, closed)
        self.set_atribute("direction", coords)

    def evento_mover(self, evento):
        if evento.get_atribute("target") in self.get_atribute("direction") and self.get_atribute("closed"):
            evento.forbid(evento.source.get_raw("OBSTACLE_IN_THE_WAY", (self.identifier, )))

    def open(self):
        super().open()
        self.refresh_salas()

    def close(self):
        super().close()
        self.refresh_salas()

    def refresh_salas(self):
        """
        Modifica el estado del objeto en todas las salas donde esta
        """
        juego = self.game
        for x in self.get_atribute("direction"):
            sala = juego.get_sala(x)
            sala.remove_entity(self)
            sala.add_entity(self)
            sala.save()

    def event_handler(self, evento):
        funciones = {"get_description": self.evento_descripcion,
                     "open": self.evento_abrir,
                     "close": self.evento_cerrar,
                     "move": self.evento_mover}
        if evento.identifier in funciones:
            funciones[evento.identifier](evento)

    def __eq__(self, other):
        if type(other) == Door and other.identifier == self.identifier \
                and self.get_atribute("direction") == other.get_atribute("direction"):
            return True
        return False
