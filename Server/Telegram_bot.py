import telebot
from multiprocessing import Manager

"""
Me gustaría guardar las ids de los chats pero parece ser que cuando se cae el bot, cambia la id
asi que cada vez que se caiga voy a tener que pedir conexion. Que le vamos a hacer
"""

m = Manager()
chat_ids = m.list()


def notify_all(txt, config):
    bot2 = telebot.TeleBot(config.get_option("telegram_token"))
    for x in chat_ids:
        print(x)
        bot2.send_message(x, txt)


def start_listening(config):

    bot = telebot.TeleBot(config.get_option("telegram_token"))

    @bot.message_handler(func=lambda message: True)
    def echo_message(message):
        chat_ids.append(message.chat.id)
        bot.send_message(message.chat.id, "Te enviaré las actualizaciones del servidor")

    bot.polling()
