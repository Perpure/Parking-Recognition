from telegram.ext import Updater
from telegram.ext import CommandHandler
import sys
import logging
import requests
import os.path
from threading import Thread
SEND_FLA = False

TOKEN = "1791644799:AAEdL0bdkPkJWfh2o0f8wvgrofi1cQs2KaY"
LINK = "t.me/park_ornull_bot"
PATH = sys.argv[1]
updater = Updater(token=TOKEN, use_context=True)

dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

F_MESSAGE = "Приветствую, чтобы подписаться на уведомления о свободных парковках на улицах Петрозаводска, нажмите /notify"


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=F_MESSAGE)


def notify(update, context):
    prev_spaces = 0
    id = 1
    while True:
        r = requests.get(os.path.join(PATH + '/get_spaces1'))
        spaces = int(r.text)
        fr = requests.get(os.path.join(PATH + '/get_frame1'))
        frame = fr.content
        file = open("sample_image.png", "wb")
        file.write(fr.content)
        file.close()
        if spaces > prev_spaces:
            loc = ''
            if id == 0:
                loc = "возле ЖД вокзала"
            elif id == 1:
                loc = "на проспекте Ленина"
            message = "Освободилось новое парковочное место " + loc
            message += f"\nВсего свободных мест: {spaces}"
            context.bot.send_message(chat_id=update.effective_chat.id, text=message)
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('sample_image.png', 'rb'))
            prev_spaces = spaces
        prev_spaces = spaces



start_handler = CommandHandler('start', start)
notify_handler = CommandHandler('notify', notify)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(notify_handler)
updater.start_polling()
updater.idle()