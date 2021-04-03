from telegram.ext import CommandHandler
from telegram.ext import Updater
import logging
from main import DATA_TO_SEND, SEND_FLAG

TOKEN = "1791644799:AAEdL0bdkPkJWfh2o0f8wvgrofi1cQs2KaY"
LINK = "t.me/park_ornull_bot"

updater = Updater(token=TOKEN, use_context=True)

dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

F_MESSAGE = "Приветствую, чтобы подписаться на уведомления о свободных парковках на улицах Петрозаводска, нажмите /notify"


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=F_MESSAGE)

def notify(update, context):
    global SEND_FLAG, DATA_TO_SEND
    while True:
        if SEND_FLAG:
            id, spaces, frame = DATA_TO_SEND
            loc = ''
            if id == 0:
                loc = "возле ЖД вокзала"
            elif id == 1:
                loc = "на просп. Ленина"
            message = "Освободилось новое парковочное место " + loc
            message += f"\nВсего свободных мест:{spaces}"
            context.bot.send_message(chat_id=update.effective_chat.id, text=message)
            SEND_FLAG = False




start_handler = CommandHandler('start', start)
notify_handler = CommandHandler('notify', notify)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(notify_handler)
updater.start_polling()
