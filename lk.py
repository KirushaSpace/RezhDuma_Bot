import telebot
from config import TOKEN
from telebot import types
import requests
import datetime
import json

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    f = open('start_message.txt', 'r', encoding='utf-8')
    markup = types.InlineKeyboardMarkup(row_width=1)
    item_log = types.InlineKeyboardButton(text='Вход', callback_data='login')
    markup.add(item_log)
    if message.from_user.is_bot:
        item_lk = types.InlineKeyboardButton(text='Личный кабинет', callback_data='lk')
        item_logout = types.InlineKeyboardButton(text='Выйти из личного кабинета', callback_data='logout')
        markup.add(item_lk, item_logout)

    item_faq = types.InlineKeyboardButton(text='Часто задаваемые вопросы', callback_data='faq')
    item_site = types.InlineKeyboardButton(text='Переход на сайт', url='http://rezh.ml/')
    markup.add(item_site, item_faq)
    bot.send_message(message.chat.id, f.read(), reply_markup=markup)
    f.close()


@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    if call.data == 'login':
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        item_log = types.InlineKeyboardButton(text='Ввести данные', callback_data='Yes')
        item_reg = types.InlineKeyboardButton(text='Не зарегистрирован?', url='http://rezh.ml/registration')
        item_back = types.InlineKeyboardButton(text='Вернуться', callback_data='back')
        keyboard.add(item_log, item_reg, item_back)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Авторизация', reply_markup=keyboard)
    elif call.data == 'lk':
        markup = types.InlineKeyboardMarkup(row_width=2)
        item_mail = types.InlineKeyboardButton(text='Почта', callback_data='mail')
        item_mes = types.InlineKeyboardButton(text='заявки', callback_data='mes')
        item_faq = types.InlineKeyboardButton(text='Часто задаваемые вопросы', callback_data='faq')
        item_back = types.InlineKeyboardButton(text='Вернуться', callback_data='back')
        markup.add(item_mail, item_mes, item_faq, item_back)
        bot.edit_message_text(message_id=call.message.message_id, chat_id=call.message.chat.id,
                              text=
                              '''Личный кабинет
                              у вас {0} новых уведомлений
                              нет изменений в проверке заявок''', reply_markup=markup)
    elif call.data == 'faq':
        print(call)
        s_faq = ''
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        item_next = types.InlineKeyboardButton(text='Дальше', callback_data='next_page')
        item_back = types.InlineKeyboardButton(text='Назад', callback_data='back_page')
        item_remove = types.InlineKeyboardButton(text='Вернуться', callback_data='del')
        keyboard.add(item_back, item_next, item_remove)
        response = open('faq.json', 'r', encoding='utf-8')
        f = json.loads(response.read())
        for i in f:
            s_faq += f"Вопрос: *{i['text']}*" + '\n'
            s_faq += f"Тип: {i['type']}" + '\n'
            appeal_date = datetime.datetime.strptime(i['appealDate'], "%Y-%m-%dT%H:%M:%S.%f")
            s_faq += f"Дата: {appeal_date.strftime('%Y.%m.%d %H:%M:%S')}" + '\n'
            s_faq += f"_Ответ: {i['response']}_" + '\n'
            s_faq += f"_От кого: {i['responsibleName']}_" + '\n'
            response_date = datetime.datetime.strptime(i['responseDate'], "%Y-%m-%dT%H:%M:%S.%f")
            s_faq += f"_Дата: {response_date.strftime('%Y.%m.%d %H:%M:%S')}_" + '\n' * 3
        bot.send_message(call.message.chat.id, s_faq, parse_mode='Markdown', reply_markup=keyboard)
    elif call.data == 'back':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        start(call.message)
    elif call.data == 'Yes':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        msg = bot.send_message(chat_id=call.message.chat.id, text='Введите логин (почту) к личному кабинету')
        bot.register_next_step_handler(msg, user_login)
    elif call.data == 'mail':
        keyboard = types.InlineKeyboardMarkup()
        item_back = types.InlineKeyboardButton(text='Вернуться', callback_data='lk')
        keyboard.add(item_back)
        bot.edit_message_text(message_id=call.message.message_id, chat_id=call.message.chat.id,
                              text='''Ваши сообщения и ответы на них
                              0 сообщений''', reply_markup=keyboard) # здесь можно будет посмотреть сообщения
    elif call.data == 'mes':
        keyboard = types.InlineKeyboardMarkup()
        item_back = types.InlineKeyboardButton(text='Вернуться', callback_data='lk')
        keyboard.add(item_back)
        bot.edit_message_text(message_id=call.message.message_id, chat_id=call.message.chat.id,
                              text='''Ваши заявки и ответы на них
                              0 сообщений''', reply_markup=keyboard)
    elif call.data == 'logout':
        k = types.InlineKeyboardMarkup(row_width=2)
        b = types.InlineKeyboardButton(text='Подтверждаю', callback_data='back')
        b1 = types.InlineKeyboardButton(text='Случайно нажал', callback_data='back')
        k.add(b, b1)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Хотите выйти?', reply_markup=k)
    elif call.data == 'del':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    # elif call.data == 'next_page':
    # elif call.data == 'back_page':




def user_login(message):
    global user_form, user_forms
    login = message.text
    # todo сделать обработчик логина
    msg = bot.send_message(message.chat.id, 'Введите пароль:')
    bot.register_next_step_handler(msg, user_password, login)


def user_password(message, login):
    password = message.text
    form = {'email': (None, login), 'password': (None, password)}
    response = requests.post('http://51.250.111.89:8080/api/login', files=form)
    bot.send_message(message.chat.id, 'Проверяю...')
    if response.status_code == 200:
        user = response.json()
        bot.send_message(message.chat.id, f"Успешный вход в систему, добро пожаловать, {user[1]['firstName']} {user[1]['lastName']}")
        markup = types.InlineKeyboardMarkup()
        item_lk = types.InlineKeyboardButton(text='Переход в личный кабинет', callback_data='lk')
        markup.add(item_lk)
        bot.send_message(message.chat.id, 'переход', reply_markup=markup)
    else:
        keyboard = types.InlineKeyboardMarkup()
        item = types.InlineKeyboardButton(text='Вернуться', callback_data='Yes')
        keyboard.add(item)
        bot.send_message(chat_id=message.chat.id, text='Неправльный ввод данных, попробуйте еще раз', reply_markup=keyboard)


@bot.message_handler(commands=['help'])
def help(message):
    cmds = open('help.txt', 'r', encoding="utf-8")
    bot.send_message(message.chat.id, cmds.read())
    cmds.close()


@bot.message_handler(commands=['persons'])
def per(message):
    global user_forms
    bot.send_message(message.chat.id, '\n'.join(user_forms))


@bot.message_handler(commands=['info'])
def information(message):
    bot.send_message(message.chat.id, message)


@bot.message_handler(content_types=["text"])
def any_msg(message):
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


bot.polling(none_stop=True)