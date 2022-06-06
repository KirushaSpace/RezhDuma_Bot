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
    g = open('users.json', 'r', encoding='utf-8')
    markup = types.InlineKeyboardMarkup(row_width=1)
    users = json.loads(g.read())
    if str(message.chat.id) not in users['tg_id'].keys():
        item_log = types.InlineKeyboardButton(text='Вход', callback_data='login')
        markup.add(item_log)
    else:
        item_lk = types.InlineKeyboardButton(text='Личный кабинет', callback_data='lk')
        markup.add(item_lk)
    item_faq = types.InlineKeyboardButton(text='Часто задаваемые вопросы', callback_data='faq')
    item_site = types.InlineKeyboardButton(text='Переход на сайт', url='http://rezh.ml/')
    markup.add(item_site, item_faq)
    bot.send_message(message.chat.id, f.read(), reply_markup=markup)
    f.close()
    g.close()


@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    if call.data == 'login':
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        item_log = types.InlineKeyboardButton(text='Ввести данные', callback_data='Yes')
        item_reg = types.InlineKeyboardButton(text='Регистрация', url='http://rezh.ml/registration')
        item_back = types.InlineKeyboardButton(text='Вернуться', callback_data='back')
        keyboard.add(item_log, item_reg, item_back)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Авторизация', reply_markup=keyboard)
    elif call.data == 'lk':
        markup = types.InlineKeyboardMarkup(row_width=2)
        f = open('users.json', 'r', encoding='utf-8')
        users = json.loads(f.read())
        if 'admin' in users['tg_id'][str(call.message.chat.id)]['roles']:
            item_mail = types.InlineKeyboardButton(text='Почта депутата', callback_data='mail')
        else:
            item_mail = types.InlineKeyboardButton(text='Почта', callback_data='mail')
        item_mes = types.InlineKeyboardButton(text='Сайт', url='http://rezh.ml/')
        item_faq = types.InlineKeyboardButton(text='Часто задаваемые вопросы', callback_data='faq')
        item_back = types.InlineKeyboardButton(text='Вернуться', callback_data='back')
        item_logout = types.InlineKeyboardButton(text='Выйти из личного кабинета', callback_data='logout')
        markup.add(item_mail, item_mes, item_faq, item_back, item_logout)
        f = open('personalAccount.txt', 'r', encoding='utf-8')
        bot.edit_message_text(message_id=call.message.message_id, chat_id=call.message.chat.id,
                              text=f.read(), reply_markup=markup)
        f.close()
    elif call.data == 'faq':
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
        f = open('users.json', 'r', encoding='utf-8')
        user = json.loads(f.read())
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        item_back = types.InlineKeyboardButton(text='Вернуться', callback_data='lk')
        keyboard.add(item_back)

        if "admin" not in user["tg_id"][str(call.message.chat.id)]["roles"]:
            mail = requests.get('http://51.250.111.89:8080/api/appeals/user?answered=&find&type&district&topic&page&count',
                                headers={'Authorization': f'Rezh {user["tg_id"][str(call.message.chat.id)]["access_token"]}'})
            text = ''
            for question in mail.json():
                text += f"Вопрос: *{question['text']}*" + '\n'
                text += f"Тип: {question['type']}" + '\n'
                appeal_date = datetime.datetime.strptime(question['appealDate'], "%Y-%m-%dT%H:%M:%S.%f")
                text += f"Дата: {appeal_date.strftime('%Y.%m.%d %H:%M:%S')}" + '\n' * 2
                if question['response']:
                    text += f"_Ответ: {question['response']}_" + '\n'
                    text += f"_От кого: {question['responsibleName']}_" + '\n'
                    response_date = datetime.datetime.strptime(question['responseDate'], "%Y-%m-%dT%H:%M:%S.%f")
                    text += f"_Дата: {response_date.strftime('%Y.%m.%d %H:%M:%S')}_" + '\n' * 3
                else:
                    text += f"_Ответа на ваше сообщение еще нет(_" + '\n' * 3
            bot.edit_message_text(message_id=call.message.message_id, chat_id=call.message.chat.id,
                                  text=text, reply_markup=keyboard, parse_mode='Markdown')
        else:
            mail = requests.get('http://51.250.111.89:8080/api/appeals/admin',
                                headers={'Authorization': f'Rezh {user["tg_id"][str(call.message.chat.id)]["access_token"]}'})
            text = 'Сообщения, на которые еще никто не ответил' + '\n' * 2
            for question in mail.json():
                if not question['response']:
                    text += f"Вопрос: *{question['text']}*" + '\n'
                    text += f"Тип: {question['type']}" + '\n'
                    text += f"От кого: {question['requester']['lastName']} {question['requester']['firstName']}" + '\n'
                    appeal_date = datetime.datetime.strptime(question['appealDate'], "%Y-%m-%dT%H:%M:%S.%f")
                    text += f"Дата: {appeal_date.strftime('%Y.%m.%d %H:%M:%S')}" + '\n' * 3
            text += "*Чтобы оставить ответ на сообщение, перейдите на сайт*"
            item_site = types.InlineKeyboardButton(text='переход на сайт в личный кабинет', url='http://rezh.ml/login')
            keyboard.add(item_site)
            bot.edit_message_text(message_id=call.message.message_id, chat_id=call.message.chat.id,
                                  text=text, reply_markup=keyboard, parse_mode='Markdown')
    elif call.data == 'logout':
        k = types.InlineKeyboardMarkup(row_width=2)
        b = types.InlineKeyboardButton(text='Подтверждаю', callback_data='logout_del')
        b1 = types.InlineKeyboardButton(text='Случайно нажал', callback_data='lk')
        k.add(b, b1)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Хотите выйти?', reply_markup=k)
    elif call.data == 'del':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    elif call.data == 'logout_del':
        kb = types.InlineKeyboardMarkup()
        g = open('users.json', 'r', encoding='utf-8')
        users = json.loads(g.read())
        user = users['tg_id'].pop(str(call.message.chat.id))
        users['email'].pop(users['email'].index(user['email']))
        d = open('users.json', 'w')
        json.dump(users, d)
        item_back = types.InlineKeyboardButton(text='Вернуться', callback_data='back')
        kb.add(item_back)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Вы успешно вышли', reply_markup=kb)


def user_login(message):
    login = message.text
    msg = bot.send_message(message.chat.id, 'Введите пароль:')
    bot.register_next_step_handler(msg, user_password, login)


def user_password(message, login):
    password = message.text
    form = {'email': (None, login), 'password': (None, password)}
    response = requests.post('http://51.250.111.89:8080/api/login', files=form)
    bot.send_message(message.chat.id, 'Проверяю...')
    if response.status_code == 200:
        user = response.json()
        g = open('users.json', 'r', encoding='utf-8')
        data = json.loads(g.read())
        if user[1]['email'] not in data['email']:
            data['email'].append(user[1]['email'])
            data['tg_id'][message.chat.id] = {
                'firstName': user[1]['firstName'],
                'lastName': user[1]['lastName'],
                'email': user[1]['email'],
                'roles': user[1]['roles'],
                'access_token': user[0]['access_token'],
            }
            with open('users.json', 'w') as users:
                json.dump(data, users)
            bot.send_message(message.chat.id, f"Успешный вход в систему, добро пожаловать, {user[1]['firstName']} {user[1]['lastName']}")
            markup = types.InlineKeyboardMarkup()
            item_lk = types.InlineKeyboardButton(text='Переход в личный кабинет', callback_data='lk')
            markup.add(item_lk)
            bot.send_message(message.chat.id, 'переход', reply_markup=markup)
            users.close()
        else:
            kb = types.InlineKeyboardMarkup()
            item = types.InlineKeyboardButton(text='Вернуться', callback_data='back')
            kb.add(item)
            bot.edit_message_text(chat_id=message.chat.id,
                                  message_id=message.message_id,
                                  text='Ваш аккаунт авторизирован на другом телеграмм аккаунте, пожалуйста выйдите, чтобы авторизироваться тут',
                                  reply_markup=kb)
        g.close()
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


@bot.message_handler(commands=['info'])
def information(message):
    bot.send_message(message.chat.id, message)


@bot.message_handler(content_types=["text"])
def any_msg(message):
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


bot.polling(none_stop=True)