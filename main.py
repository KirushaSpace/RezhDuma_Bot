import telebot
import config
from telebot import types

bot = telebot.TeleBot(config.TOKEN)
persons = []
person = [0] * 2


@bot.message_handler(commands=['start'])
def start(message):
    global persons
    name = message.from_user.first_name
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = [types.InlineKeyboardButton(text='Вход', callback_data='login'),
               types.InlineKeyboardButton(text='Переход на сайт', url='https://www.youtube.com/watch?v=dQw4w9WgXcQ')]
    if message.from_user.id in persons:
        buttons.append(types.InlineKeyboardButton(text='Личный кабинет', callback_data='lk'))
    markup.add(buttons)
    bot.send_message(message.chat.id,
                     '\n'.join(map(lambda str: str.strip(), f'''Привет, {name}, я твой помощник!
                         пару слов туда-сюда
                         действия, которые вы можете совершить'''.split('\n'))), reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    if call.data == 'login':
        msg = bot.send_message(call.message.chat.id, 'Введите ваш логин:')
        bot.register_next_step_handler(msg, user_login)
    elif call.data == 'site':
        bot.send_message(call.message.chat.id, 'щас закину')
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        button = types.KeyboardButton('Вернуться')
        markup.add(button)
        msg = bot.send_message(call.message.chat.id, 'хер там, сайта еще нет', reply_markup=markup)
        bot.register_next_step_handler(msg, start)
    elif call.data == 'lk':
        markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
        buttons = [types.KeyboardButton(text='Почта'),
                   types.KeyboardButton(text='заявки')]
        markup.add(buttons)
        bot.send_message(call.message.chat.id, 'Выберете куда вы хотите перейти', reply_markup=markup)



def user_login(message):
    login = message.text
    # todo сделать обработчик логина
    global person
    person[0] = login
    msg = bot.send_message(message.chat.id, 'Введите пароль:')
    bot.register_next_step_handler(msg, user_password)


def user_password(message):
    password = message.text
    global person, persons
    person[1] = password
    if person not in persons:
        persons.append([person[0], person[1], message.from_user.id])
    # todo обработчик пароля
    # todo проверка есть ли пользователь в системе
    bot.send_message(message.chat.id, 'Проверяю...')
    bot.send_message(message.chat.id, 'Успешный вход в систему, добро пожаловать, {Имя} {Фамилия}')
    bot.send_message(message.chat.id, 'А все, тут функционал закончился')


@bot.message_handler(commands=['help'])
def help(message):
    cmds = open('help.txt', 'r', encoding="utf-8")
    bot.send_message(message.chat.id, cmds.read())


@bot.message_handler(commands=['persons'])
def per(message):
    global persons
    bot.send_message(message.chat.id,
                     '\n'.join(map(lambda x: f'{x[0]} {x[1]} {x[2]}', persons)))


@bot.message_handler(commands=['info'])
def information(message):
    bot.send_message(message.chat.id, message)


bot.polling(none_stop=True)