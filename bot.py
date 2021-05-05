from telegram.ext import Updater, CommandHandler
from db import get_data_by_date, date
from pprint import pprint
import envs


def hello(update, context):
    result = get_data_by_date(date.today())
    pprint(result)
    update.message.reply_text(str(result))


updater = Updater(envs.TOKEN)

updater.dispatcher.add_handler(CommandHandler('hello', hello))

print('Starting bot...')
updater.start_polling()
updater.idle()
