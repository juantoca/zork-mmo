from socket import error as socket_error
from socket import timeout as timeout_error
from socket import socket
from time import sleep, time

from Crypt_Server.Server import DisconnectedClient, InvalidToken, UnableToDecrypt, Connection, Server, KeyExchangeFailed
from Crypto.Hash import SHA3_256

from Server.Object_pickler import guardar, cargar
from peewee import *

from Server.Game import Game
from Server.Objects.User import Personaje

from Server.Config import Archivo

db = SqliteDatabase("Users.db")


class Usuario(Model):
    """
    Modelo para la tabla Usuario
    """
    nick = CharField(max_length=20, unique=True)
    password_hash = CharField()
    last_connection = IntegerField()
    ip = CharField(max_length=10)
    objeto = BareField()

    class Meta:
        database = db


def handle_login(conn: socket, game: Game, server: Server, config: Archivo):
    """
    Maneja una conexión entrante
    :param conn: Conexión
    :param game: Game object
    :param server: Server object
    :param config: Configuración del servidor
    """
    timeout = float(config.get_option("timeout"))
    connection_cooldown = float(config.get_option("delay"))
    try:
        conn = server.key_exchange(conn, timeout)
        conn.set_query_cooldown(connection_cooldown)
        dic = {"REGISTER": register, "LOGIN": login}
        command = conn.recv(timeout).split(" ")
        if len(command) == 3 and command[0] in dic:
            success = dic[command[0]](conn, game, command, config)
            if not success:
                conn.close()
        else:
            conn.send("TOKEN INVALID_COMMAND")
            conn.close()
    except timeout_error:
        if type(conn) == Connection:
            conn.send("TOKEN TIMED_OUT_DISCONNECTION")
        else:
            conn.send(b"TOKEN TIMED_OUT_DISCONNECTION")
        conn.close()
    except (DisconnectedClient, InvalidToken, UnableToDecrypt, socket_error, KeyExchangeFailed):
        pass


def pass_validation(passwd: str) -> bool:
    """
    Valida la contraseña
    :param passwd: Password a validar
    :return: Es válida?
    """
    if len(passwd) < 8:
        return False
    return True


def parse_string(string: str, forbidden_chars: tuple = (" ", ";", "-", "·")) -> bool:
    """
    Aunque peewee no tenga SQL injection ya que las queries estan parametrizadas, hay ciertos carácteres
    que por protocolo en los comandos pueden ser molestos(sobretodo los espacios)
    :param string: String a parsear
    :param forbidden_chars: Carácteres prohibidos
    :return: Es válida la string?
    """
    for x in forbidden_chars:
        if x in string:
            return False
    return True


def nick_validation(nick: str, nick_parser: callable=parse_string) -> bool:
    """
    Comprueba que el nick es válido
    :param nick: Nick a validar
    :param nick_parser: String parser
    :return: Valid nick?
    """
    if len(nick) > 20 or not nick_parser(nick):
        return False
    return True


def register(conn: Connection, game: Game, command: (list, tuple), config, user_object=Personaje,
             valid_nick_func: callable=nick_validation, valid_passwd_func: callable=pass_validation,
             ) -> bool:
    """
    Protocolo para registrar un usuario
    :param conn: Objeto representando la conexión
    :param game: Game Handler
    :param command: Comando en formato iterable ("REGISTER", nick, contraseña)
    :param user_object: Objeto que inicializar
    :param valid_nick_func: Funcion con la que verificar la validez del nick
    :param valid_passwd_func: Funcion con la que verificar la validez de la contraseña
    :return: Succesful?
    """
    command = command[1:]  # [nick, contraseña]
    if not valid_nick_func(command[0]):
        conn.send("TOKEN INVALID_NICK")
        return False
    if get_user_object(command[0], config) is not None:
        conn.send("TOKEN NICK_TAKEN")
        return False
    if not valid_passwd_func(command[1]):
        conn.send("TOKEN INVALID_PASSWORD")
        return False
    ip = len(Usuario.select(Usuario.ip == conn.get_conn().getpeername()[0]))
    if ip >= int(config.get_option("maximum_accounts_per_ip")):
        conn.send("TOKEN TAKEN_IP")
        return False
    hasheo = SHA3_256.new(bytes(command[1], "utf-8")).hexdigest()
    usuario = user_object(command[0], initial_coords=(0, 0, 0))
    objeto = guardar(usuario, config)
    Usuario.create(nick=command[0], password_hash=hasheo, objeto=objeto,
                   last_connection=int(time()), ip=conn.get_conn().getpeername()[0])
    game.add_query(conn, usuario)
    sleep(1)  # Este sleep evita que el contador de referencias del objeto socket caiga a cero y se cierre antes
    #  que el proceso de Game tenga su copia funcional. Es probable que esto no funcione asi pero funciona asi que
    # no lo toques
    return True


def login(conn: Connection, game: Game, command: (list, tuple), config:Archivo,
          nick_parser: callable=parse_string) -> bool:
    """
    Función que permite a una conexión entrar al juego con una cuenta ya existente
    :param conn: Conexión con el cliente
    :param game: Game Handler
    :param command: Comando en formato iterable ("LOGIN", nick, contraseña)
    :param nick_parser: Function to parse the given nick
    :return Succesful?
    """
    command = command[1:]  # [nick, contraseña]
    if not nick_parser(command[0]):
        conn.send("TOKEN INVALID_NICK")
        return False
    objeto = get_user_object(command[0], config)
    if objeto is None:
        conn.send("TOKEN NICK_DOESNT_EXIST")
        return False
    registro = Usuario.select().where(Usuario.nick == command[0]).get()
    registro.last_connection = int(time())
    password = SHA3_256.new(bytes(command[1], "utf-8")).hexdigest()
    if password != registro.password_hash:
        conn.send("TOKEN INVALID_PASSWORD")
        return False
    game.add_query(conn, get_user_object(command[0], config))
    sleep(1)
    return True


def change_passwd(user, current: str, new: str, game, conn):
    """
    Cambia la contraseña de el usuario especificado
    :param user: Usuario a modificar
    :param current: Contraseña actual
    :param new: Nueva contraseña
    :param game: Game object
    :param conn: Conexion con el usuario
    """
    registro = Usuario.select().where(Usuario.nick == user.nick).get()
    hasheo = SHA3_256.new(bytes(current, "utf-8")).hexdigest()
    if hasheo != registro.password_hash:
        user.send(game, conn, "INCORRECT_PASSWORD")
    else:
        registro.password_hash = SHA3_256.new(bytes(new, "utf-8")).hexdigest()
        registro.save()


def get_user_object(nick: str, config:Archivo) -> Personaje:  # TODO Encriptar objetos en la base de datos
    """
    Carga un usuario de la base de datos
    :param nick: Nick a buscar
    :return: Objeto personaje o None si no existe el usuario especificado
    """
    try:
        return cargar(Usuario.select().where(Usuario.nick == nick).get().objeto, config)
    except Usuario.DoesNotExist:
        return None


def set_user_object(nick: str, objeto: Personaje, config:Archivo) -> bool:
    """
    Vuelca un usuario a la base de datos
    :param nick: Nick del usuario
    :param objeto: Objeto usuario
    :return: Success?
    """
    try:
        obj = Usuario.select().where(Usuario.nick == nick).get()
        obj.objeto = guardar(objeto, config)
        obj.save()
        return True
    except Usuario.DoesNotExist:
        return False


if len(db.get_tables()) == 0:
    db.create_table(Usuario)
