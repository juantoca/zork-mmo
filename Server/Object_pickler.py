from pickle import dumps, loads
from Crypto.Cipher import ChaCha20
from Crypto.Random import get_random_bytes
from time import sleep
from subprocess import call

"""
Es probable que este archivo se pudiera incluir en otra parte pero a lo mejor en el futuro quiero cambiar
el sistema de guardado(El pickle ocupa bastante espacio)
"""


def guardar(objeto, config):
    string = bytes(dumps(objeto))
    clave = config.get_option("cryptographic_key_db")
    cipher = ChaCha20.new(key=clave)
    return cipher.nonce + cipher.encrypt(string)


def cargar(objeto, config):
    secret = config.get_option("cryptographic_key_db")
    msg_nonce = objeto[:8]
    ciphertext = objeto[8:]
    cipher = ChaCha20.new(key=secret, nonce=msg_nonce)
    objeto = cipher.decrypt(ciphertext)
    return loads(objeto)


def generate_key(config):
    try:
        open("Salas.db", "r")
        open("Users.db", "r")
    except:
        key = get_random_bytes(int(256/8))
        print("No se ha encontrado las bases de datos. Hemos generado una clave"
              "criptográfica para usarla. Almacenela ya que "
              "para volver a levantar el "
              "servidor se requiere para desencriptar la base de datos. La clave es la"
              "siguiente:\n\n"+key.hex()+"\n\nEste mensaje se borrara en 10 segundos")
        sleep(10)
    else:
        key = bytes.fromhex(input("Introduzca la clave de encriptación para las bases de datos\n->"))

    config.set_option("cryptographic_key_db", key)
    call("reset")  # Borramos los datos sensibles de la terminal

