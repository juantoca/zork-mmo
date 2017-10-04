import Crypt_Server.Server
from multiprocessing import Process, Value
from socket import timeout
from Server.Game import Game
from time import time
import logging
from time import ctime


def main(ip: str, port: int, exit_var: Value, log_func_handler: callable, game: Game,
         time_elapse: int=1) -> None:
    dic = {}  # ip : instante de ultima conexion
    logging.info("Levantando servidor. Generando clave criptográfica")
    server = Crypt_Server.Server.Server(ip, port)
    logging.info("Servidor levantado y escuchando en "+ip+":"+str(port))
    while exit_var.value is False:
        try:
            conn = server.accept(timeout=1)
            instante = time()
            keys = list(dic.keys())
            for ip in keys:
                if instante - dic[ip] > time_elapse:
                    del dic[ip]

            ip = conn.getpeername()[0]
            if ip not in dic:
                dic[ip] = time()
                p = Process(target=log_func_handler, args=(conn, game, server))
                p.start()
            else:
                dic[ip] = time()
                logging.warning(ip + " a mandado demasiadas peticiones. Denegación de servicios?")
        except IOError:
            pass
        except timeout:
            pass
        except Exception:
            logging.exception(ctime())
            exit_var.value = True
    logging.warning("El servidor dejó de escuchar conexiones")
