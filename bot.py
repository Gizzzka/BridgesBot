from telegram.ext import Updater, CommandHandler
from envs import TOKEN


def hello(update, context):
    update.message.reply_text(f'Hello {update.effective_user.first_name}')


updater = Updater(TOKEN)

updater.dispatcher.add_handler(CommandHandler('hello', hello))

updater.start_polling()
updater.idle()
