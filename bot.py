from telegram.ext import Updater
from telegram.ext import CommandHandler
import logging
import requests
import telebot
from threading import Thread
SEND_FLA = False

TOKEN = "1791644799:AAEdL0bdkPkJWfh2o0f8wvgrofi1cQs2KaY"
LINK = "t.me/park_ornull_bot"

updater = Updater(token=TOKEN, use_context=True)

dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

F_MESSAGE = "Приветствую, чтобы подписаться на уведомления о свободных парковках на улицах Петрозаводска, нажмите /notify"


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=F_MESSAGE)

def check_new_place():
    global SEND_FLA
    r = requests.get('/get_spaces1')
    spaces = r.text
    if spaces > PREV_SPACES and spaces > 0:
        DATA_TO_SEND[0] = id
        DATA_TO_SEND[1] = spaces
        DATA_TO_SEND[2] = img
        PREV_SPACES = spaces
        SEND_FLA = True


def notify(update, context):
    while True:
        global DATA_TO_SEND, SEND_FLA
        if SEND_FLA:
            id, spaces, frame = DATA_TO_SEND
            loc = ''
            if id == 0:
                loc = "возле ЖД вокзала"
            elif id == 1:
                loc = "на просп. Ленина"
            message = "Освободилось новое парковочное место " + loc
            message += f"\nВсего свободных мест: {spaces}"
            context.bot.send_message(chat_id=update.effective_chat.id, text=message)
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(frame, 'rb'))
            SEND_FLA = False



start_handler = CommandHandler('start', start)
notify_handler = CommandHandler('notify', notify)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(notify_handler)
updater.start_polling()
updater.idle()