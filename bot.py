from telegram.ext import Updater, CommandHandler
from envs import TOKEN
from datetime import date
from db import get_data_by_date


def hello(update, context):
    result = get_data_by_date(date.today())
    update.message.reply_text(str(result))


updater = Updater(TOKEN)

updater.dispatcher.add_handler(CommandHandler('hello', hello))

print('Starting bot...')
updater.start_polling()
updater.idle()
