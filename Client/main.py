import Crypt_Client.Client
from multiprocessing import Process
from multiprocessing import Manager
from time import sleep


class Client:

    def __init__(self, ip, puerto, claves=None):
        self.conn = Crypt_Client.Client.Client(ip, puerto, None, claves=claves)

    def run(self):
        m = Manager()
        salir = m.Value(bool, False)
        p = Process(target=self.listener, args=(salir, ))
        p.start()
        self.speaker(salir)

    def listener(self, salir):
        while not salir.value:
            msg = self.conn.recv()
            print(msg)

    def speaker(self, salir):
        #self.conn.send("LOGIN proof 12345678")
        while not salir.value:
            self.conn.send(input(""))


cliente = Client("localhost", 8000)
cliente.run()
