import multiprocessing
from queue import Empty
from time import time
from Server.Config import Languages

from Server.Objects.User import Personaje

from Crypt_Server.Server import DisconnectedClient, TooManyQueries, InvalidToken, UnableToDecrypt

from Server.World_Handler import get_sala_object

from logging import info, warning, debug


class Game:

    def __init__(self, refresh_rate=60, save_rate=60*60):
        m = multiprocessing.Manager()
        self.languages = Languages()
        self.queue = m.Queue()
        self.salas = {}  # coordenadas: Sala
        self.users = {}  # nick : Personaje
        self.last_refresh = time()
        self.last_save = time()
        self.refresh_rate = refresh_rate
        self.save_rate = save_rate

    def run(self):
        """
        LOOP DEL JUEGO
        """
        empty = False
        while not empty:  # Añadimos usuarios que esten en la cola de loggeo
            try:
                self.add_user(*self.queue.get_nowait())
            except Empty:
                empty = True
        self.run_commands()  # Ejecutamos comandos
        if time() - self.last_refresh > self.refresh_rate:
            debug("Cambio de ciclo")
            for x in self.salas.values():
                x.update()
            self.last_refresh = time()
        if time() - self.last_save > self.save_rate:
            info("Volcando datos a disco")
            for x in self.users.values():
                x[1].send(self, x, "SAVING_DATA")
            self.save_all()
            self.last_save = time()

    def get_sala(self, coords):
        if coords in self.salas:
            return self.salas[coords]
        else:
            return get_sala_object(coords)

    def move_user(self, user, coords):
        sala = self.get_sala(coords)
        sala.add_user(user)
        self.salas[sala.coordenadas] = sala
        vieja = self.get_sala(user.coords)
        vieja.remove_user(user)
        if len(vieja.usuarios) == 0:
            self.descargar_sala(vieja)
        user.coords = coords
        user.sala = sala
        debug("Salas cargadas: " + str(len(self.salas)))

    def send_all(self, msg):
        """
        Manda un mensaje a todos los usuarios
        :param msg: Mensaje a mandar
        """
        for x in self.users.values():
            x.conn.send(msg)

    def run_commands(self):
        """
        Recorre todos los usuarios en busca de comandos que ejecutar
        """
        # BUSY W8ING??? You piece of shit!!!
        # La verdad es que no se me ocurria otra manera
        # MENTIROSO Lo puedes hacer por threads
        # Soy un vago. Eso es lo que querías que dijera?
        # Me vale
        valores = list(self.users.values())
        for x in valores:
            try:
                x.handle_command(x.conn.recv(0))
            except DisconnectedClient:
                info(x.nick + " se ha desconectado")
                self.descargar_usuario(x)
            except (IOError, UnableToDecrypt, InvalidToken, TooManyQueries):
                # Si hay algún error en la conexión pasamos(En caso de algún tipo de corrupción
                # no queremos desconectar al cliente)
                pass

    def add_query(self, conn, objeto):
        """
        Función que permite que otros procesos pidan añadir personajes al juego
        :param conn: Conexión con el cliente
        :param objeto: Objeto de personaje
        """
        self.queue.put((conn, objeto))

    def add_user(self, conn, objeto: Personaje):  # TODO Usuario Root
        """
        Función que hace efectiva la petición de añadir el personaje
        :param conn: Conexión con el cliente
        :param objeto: Objeto de personaje
        """
        coords = objeto.coords
        if objeto.nick in self.users:
            self.users[objeto.nick].save()
        if coords not in self.salas:
            sala = get_sala_object(objeto.coords)
            if sala is None:
                conn.send("TOKEN SPAWN_POINT_DISSAPEARED")
                warning("Las coordenadas de inicio del jugador " + objeto.nick + " no contienen ninguna sala")
                conn.close()
                return
            self.salas[coords] = sala
        sala = self.salas[coords]
        sala.add_user(objeto)
        objeto.conn, objeto.game, objeto.sala = conn, self, sala
        self.users[objeto.nick] = objeto
        info(objeto.nick + " se ha conectado")
        conn.send("TOKEN LOGIN_COMPLETED")

    def save_all(self):
        """
        Guardamos todos los datos a la base de datos sin descargarlos
        """
        for x in self.users.values():
            x.save()
        for x in self.salas.values():
            x.save()

    def descargar_sala(self, sala):
        """
        Descargamos una sala dada a la base de datos
        :param sala: Objeto Sala a descargar
        """
        sala.save()
        del self.salas[sala.coordenadas]

    def descargar_usuario(self, objeto):
        """
        Descargamos el usuario dado a la base de datos
        :param objeto: Objeto Personaje
        """
        objeto.save()
        sala = self.salas[objeto.coords]
        users = sala.usuarios
        del users[objeto.nick]
        if len(users) == 0:
            self.descargar_sala(sala)
        self.users[objeto.nick].conn.close()
        del self.users[objeto.nick]

    def descargar_todo(self):
        """
        Descargamos todas las entidades a la base de datos para cerrar el servidor
        """
        info("Volcando datos a disco")
        usuarios = list(self.users.values())
        for x in usuarios:
            self.descargar_usuario(x)
        salas = list(self.salas.values())
        """No debería ser necesario descargar las salas explícitamente pero, ya que este método no requiere gran
        eficiencia, podemos hacerlo para evitar pérdidas de datos"""
        for x in salas:
            self.descargar_sala(x)

    def __del__(self):
        """
        Ya sabemos que los destructores en python no son muy fiables así que no se debería confiar en la
        destrucción implícita si es posible
        """
        self.descargar_todo()
