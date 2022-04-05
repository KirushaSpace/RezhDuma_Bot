import telebot
from telebot import types

TOKEN = '5289190892:AAEizjNTS96yAz0rxdQiyKImRBWq4boLllo'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(info):
    name = info.from_user.first_name
    bot.send_message(info.chat.id, f'Привет, {name}, я твой помощник!')


@bot.message_handler(commands=['help'])
def help(info):
    comms = open('help.txt', 'r', encoding="utf-8")
    bot.send_message(info.chat.id, comms.read())


bot.polling(none_stop=True)