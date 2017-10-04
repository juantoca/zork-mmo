import logging
import multiprocessing
from time import ctime

import Server.Login
from Server.Game import Game

import Server.Connections as Connections


def main():
    formater = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
    terminal = logging.StreamHandler()
    terminal.setFormatter(formater)
    files = logging.FileHandler("./logs/"+ctime()+".log")
    files.setFormatter(formater)
    root = logging.getLogger()
    root.addHandler(terminal)
    root.addHandler(files)
    root.level = 20

    m = multiprocessing.Manager()
    salir = m.Value("b", False)

    game = Game()

    p = multiprocessing.Process(target=Connections.main,
                                args=("localhost", 8001, salir, Server.Login.handle_login, game))
    p.start()

    q = multiprocessing.Process(target=loop, args=(salir, game))
    q.start()

    p.join()
    q.join()


def loop(salir, game):
    try:
        while not salir.value:
            game.run()
    except Exception:
        salir.value = True
        game.send_all("UNEXPECTED_INTERNAL_ERROR")
        game.descargar_todo()
        logging.exception(ctime())


if __name__ == "__main__":
    main()
