

class Entity:

    def __init__(self, identifier, upper_object=None):
        self.identifier = identifier
        self.entities = {}
        """Todas las entidades pueden contener otras entidades de tal forma que se puede modificar el comportamiento
        de una entidad simplemente añadiendo sub-entidades. Por ejemplo, un cofre se podrá abrir de normal y sin
        necesidad de redefinir cofre en el caso de querer añadirle un cerrojo podemos añadirle una sub entidad 
        que incluya requerimientos para abrir el cofre"""

        self.upper_object = upper_object
        """Para que el método antes expuesto funcione, necesitamos una referencia cruzada hacia la clase superior.
        Nos impedirá usar el método __del__ para guardar los datos implicitamente pero a cambio obtendremos una
        gran escalabilidad en el proyecto"""
        self.atributes = {}

    def evento(self, event_object):
        """
        Método que modifica un objeto de tipo Evento para su posterior ejecución
        :param event_object: Objeto Evento
        """
        entidades = list(self.entities.values())
        for x in entidades:
            x.evento(event_object)

    def update(self):
        """
        Método que se ejecuta en las entidades a cada ciclo de juego
        """
        entidades = list(self.entities.values())
        for x in entidades:
            x.update()

    def prepare_save(self):
        """
        Método que prepara las entidades para ser guardadas en disco
        """
        entidades = list(self.entities.values())
        for x in entidades:
            x.prepare_save()

    def query_entity(self, identifier):
        """
        Busca una entidad recursivamente
        :param identifier: Identificador de la entidad
        :return: None si no se ha encontrado ninguna sub-entidad. Object si se ha encontrado
        """
        if identifier in self.entities:
            return self.entities[identifier]
        if len(self.entities) == 0:
            return None
        values = list(self.entities.values())
        for x in values:
            query = x.query_entity(identifier)
            if query is not None:
                return query
        return None

    def add_entity(self, entity, force=False, set_upper=True):
        """
        Añade una sub-entidad
        :param entity: Entidad a añadir
        :param force: Forzar la sobrescritura?
        """
        if entity.identifier not in self.entities or force:
            if set_upper:
                entity.set_upper_object(self)
            self.entities[entity.identifier] = entity
        else:
            raise KeyError("Se ha intentado sobreescribir una entidad")

    def remove_entity(self, entity):
        """
        Destruye una sub-entidad
        :param entity: Entidad a destruir
        """
        del self.entities[entity.identifier]

    def get_upper_object(self):
        return self.upper_object

    def set_upper_object(self, entity):
        self.upper_object = entity

    def parse_command(self, user, command):
        pass

    def exec_command(self, user, command):
        """
        Ejecuta busca una entidad que soporte el comando especificado
        :param user: Objeto personaje que a enviado el comando
        :param command: Comando a ejecutar
        """
        if self.parse_command(user, command):
            return True
        values = list(self.entities.values())
        for x in values:
            if x.exec_command(user, command):
                return True
        return False

    def get_atribute(self, token):
        """
        Obtiene un atributo del objeto
        :param token: Atributo a devolver
        :return: Valor del atributo
        """
        if token in self.atributes:
            return self.atributes[token]
        return False

    def set_atribute(self, token, value):
        """
        Escribe un atributo en la entidad
        :param token: Atributo a escribir
        :param value: Valor del atributo
        """
        self.atributes[token] = value

    def remove_atribute(self, token):
        if token in self.atributes:
            del self.atributes[token]
