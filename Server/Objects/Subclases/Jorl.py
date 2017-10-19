
from Server.Objects.Entity import Entity

"""
Clase de prueba
"""


class Jorl(Entity):

    def __init__(self, identifier, identity_type, description=""):
        super().__init__(identifier, identity_type)
        self.description = description

    def get_description(self):
        return self.description
