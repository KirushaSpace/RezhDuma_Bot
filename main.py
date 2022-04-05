import telebot
from telebot import types

bot = telebot.TeleBot('5289190892:AAEizjNTS96yAz0rxdQiyKImRBWq4boLllo')

@bot.message_handler(commands=['start'])
def start(info):
    mess = info.from_user.first_name
    markup = types.ReplyKeyboardRemove()
    bot.send_message(info.chat.id, f'Привет, {mess}, я твой помощник!', reply_markup=markup)


@bot.message_handler(commands=['help'])
def help(info):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    website = types.KeyboardButton('Веб сайт')
    start_b = types.KeyboardButton('/start')
    markup.add(website, start_b)
    bot.send_message(info.chat.id, 'Что я могу', reply_markup=markup)


bot.polling(none_stop=True)