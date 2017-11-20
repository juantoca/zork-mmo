import Crypt_Server.Server
from multiprocessing import Process, Value
from socket import timeout
from Server.Game import Game
from time import time
import logging
from time import ctime
from Server.Config import Archivo


def main(ip: str, port: int, exit_var: Value, log_func_handler: callable, game: Game,
         config: Archivo) -> None:
    # TODO Modificar el sistema de hilos evitando procesos del sistema para evitar fork bombs provocadas por DDOS
    """
    Inicializa el servidor e inicializa las conexiones
    :param ip: Ip del servidor a levantar
    :param port: Puerto del servidor
    :param exit_var: Condición de salida
    :param log_func_handler: Función de control del logger
    :param game: Objeto juego al que añadir las nuevas conexiones
    :param config: Configuración del servidor
    """
    time_elapse = float(config.get_option("minimum_secs"))
    dic = {}  # ip : instante de ultima conexion
    logging.info("Levantando servidor. Generando clave criptográfica")
    server = Crypt_Server.Server.Server(ip, port)  # Levantamos el servidor
    logging.info("Servidor levantado y escuchando en "+ip+":"+str(port))
    while exit_var.value is False:
        try:
            conn = server.accept(timeout=time_elapse)  # Ponemos timeout para refrescar de vez en cuando la lista de ips
            instante = time()
            ips = list(dic.keys())
            for ip in ips:  # Actualizamos baneos temporales
                if instante - dic[ip] > time_elapse:
                    del dic[ip]

            ip = conn.getpeername()[0]
            if ip not in dic:  # Si no ha mandado una petición recientemente la aceptamos
                dic[ip] = time()
                p = Process(target=log_func_handler, args=(conn, game, server, config))
                p.start()
            else:  # Si la ha enviado notificamos al servidor
                dic[ip] = time()
                logging.warning(ip + " a mandado demasiadas peticiones. ¿Denegación de servicios?")
        except IOError:
            pass
        except timeout:
            pass
        except Exception:
            logging.exception(ctime())
            exit_var.value = True
    logging.warning("El servidor dejó de escuchar conexiones")
