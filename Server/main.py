import logging
import multiprocessing
from time import ctime, sleep
import Server.Connections as Connections

from Server.Config import Archivo

from Server.Object_pickler import generate_key


def main():
    formater = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")  # Inicializamos el logger
    terminal = logging.StreamHandler()
    terminal.setFormatter(formater)
    files = logging.FileHandler("./logs/"+ctime()+".log")
    files.setFormatter(formater)
    root = logging.getLogger()
    root.addHandler(terminal)
    root.addHandler(files)
    root.level = 20

    config = Archivo("./config.conf")  # Cargamos la configuración del servidor

    generate_key(config)
    m = multiprocessing.Manager()
    salir = m.Value("b", False)  # Variable de salida del programa

    import Server.Login
    from Server.Game import Game

    game = Game(config)  # Juego propiamente dicho

    p = multiprocessing.Process(target=Connections.main,
                                args=(config.get_option("ip"), int(config.get_option("port")),
                                      salir, Server.Login.handle_login, game, config))
    p.start()  # Aceptar peticiones de logeo o registro

    q = multiprocessing.Process(target=loop, args=(salir, game))
    q.start()

    p.join()
    q.join()


def loop(salir, game):
    try:
        while not salir.value:
            game.run()
            sleep(0.01)  # Bajamos el uso de la cpu a lo bruto
    except Exception:
        salir.value = True
        game.send_all("UNEXPECTED_INTERNAL_ERROR")
        game.descargar_todo()  # Volcamos a disco todos los datos
        logging.exception(ctime())  # Guardamos las excepción
        # TODO mandar notificación al administrador(correo, telegram, etc..)


if __name__ == "__main__":
    main()
