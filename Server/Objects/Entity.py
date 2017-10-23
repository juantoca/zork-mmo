

class Entity:

    def __init__(self, identifier, identity_type, upper_object=None):
        self.identifier = identifier
        self.identity_type = identity_type
        self.entities = []
        """Todas las entidades pueden contener otras entidades de tal forma que se puede modificar el comportamiento
        de una entidad simplemente añadiendo sub-entidades. Por ejemplo, un cofre se podrá abrir de normal y sin
        necesidad de redefinir cofre en el caso de querer añadirle un cerrojo podemos añadirle una sub entidad 
        que incluya requerimientos para abrir el cofre"""

        self.upper_object = upper_object
        """Para que el método antes expuesto funcione, necesitamos una referencia cruzada hacia la clase superior.
        Nos impedirá usar el método __del__ para guardar los datos implicitamente pero a cambio obtendremos una
        gran escalabilidad en el proyecto"""
        self.atributes = {}

    def search_type(self, type_identifier):
        returneo = []
        if self.identity_type == type_identifier:
            returneo.append(self)
        for x in self.get_entities():
            returneo += x.search_type(type_identifier)
        return returneo

    def evento(self, event_object):
        """
        Método que modifica un objeto de tipo Evento para su posterior ejecución
        :param event_object: Objeto Evento
        """
        for x in self:
            x.evento(event_object)

    def get_entities(self):
        return [x for x in self.entities if not x.get_atribute("hidden")]

    def update(self):
        """
        Método que se ejecuta en las entidades a cada ciclo de juego
        """
        for x in self:
            x.update()

    def prepare_save(self):
        """
        Método que prepara las entidades para ser guardadas en disco recursivamente
        """
        for x in self:
            x.prepare_save()

    def has_instance(self, instance):
        """
        Devuelve si una entidad esta contenida en esta
        :param instance: Instancia de la entidad
        :return: Esta contenida? Boolean
        """
        if instance == self:
            return True
        for x in self.entities:
            if x.has_instance(instance):
                return True
        return False

    def query_entity(self, identifier):
        """
        Busca una entidad recursivamente
        :param identifier: Identificador de la entidad
        :return: Lista de entidades que responden al identifier
        """
        returneo = []
        if identifier == self.identifier:
            returneo.append(self)
        for x in self.get_entities():
            returneo += x.query_entity(identifier)
        return returneo

    def add_entity(self, entity, set_upper=True):
        """
        Añade una sub-entidad
        :param entity: Entidad a añadir
        :param set_upper: Debo guardar la clase que la contiene?
        """
        if set_upper:
            entity.set_upper_object(self)
        self.entities.append(entity)

    def remove_entity(self, entity):
        """
        Destruye una sub-entidad
        :param entity: Entidad a destruir
        """
        self.entities.remove(entity)

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
        for x in self:
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

    def __iter__(self):
        """
        Itera a través de todas las entidades
        :return: Entidad actual
        """
        for x in self.entities:
            yield x
