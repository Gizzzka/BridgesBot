from Demo_db import Operator
from telegram.ext import Updater
from telegram.ext import MessageHandler, CommandHandler, Filters
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import logging
import pprint

token = '1760883122:AAHNfTbFc2VGq130wolzSnoilAMNVkcpP6U'
updater = Updater(token=token)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def start(update, context):
    custom_keyboard = [['Мост Александра Невского'],
                       ['Биржевой мост', 'Благовещенский мост'],
                       ['Большеохтинский мост', 'Володарский мост'],
                       ['Дворцовый мост', 'Литейный мост'],
                       ['Троицкий мост', 'Тучков мост']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Привет!\nЯ помогу тебе узнать, какие мосты сегодня разводятся\nДля этого тебе '
                                  'достаточно выбрать название моста из списка',
                             reply_markup=reply_markup)


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


def fix_info(info):
    title = ''
    time_dict = {}

    for bridge_title in info:
        title = bridge_title
        for time in info[bridge_title].keys():
            time_dict[time] = info[bridge_title][time]

    if len(time_dict) == 0:
        return f'{title} сегодня не разводится'

    final = f'{title}:\n'
    for opening_time in time_dict:
        final += f'разведен с {str(opening_time)[:-3]} по {str(time_dict[opening_time])[:-3]}'
        final += '\nтакже, '

    return final[:-8]


def bridge(update, context):
    try:
        bridge_title = update.message.text
        operator = Operator()
        result = operator.get_data_by_title(bridge_title)
        result = fix_info(result)
        context.bot.send_message(chat_id=update.effective_chat.id, text=result)

    except Exception as ex:
        print(ex)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Сегодня этот мост не разводится!')


def create_from_scratch(update, context):
    operator = Operator()
    operator.create_db()
    operator.fill_data()
    context.bot.send_message(chat_id=update.effective_chat.id, text='Новая база данных была создана')


def update_info(update, context):
    operator = Operator()
    operator.fill_data()
    context.bot.send_message(chat_id=update.effective_chat.id, text='Данные в базе данных были обновлены')


scratch_handler = CommandHandler('create_from_scratch', create_from_scratch)
dispatcher.add_handler(scratch_handler)

update_handler = CommandHandler('update_info', update_info)
dispatcher.add_handler(update_handler)

bridge_handler = MessageHandler(Filters.text, bridge)
dispatcher.add_handler(bridge_handler)

updater.start_polling()
