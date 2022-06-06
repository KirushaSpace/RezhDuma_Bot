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
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Авторизация',
                              reply_markup=keyboard)
    elif call.data == 'lk':
        markup = types.InlineKeyboardMarkup(row_width=2)
        f = open('users.json', 'r', encoding='utf-8')
        users = json.loads(f.read())
        if 'ADMIN' in users['tg_id'][str(call.message.chat.id)]['roles']:
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
        response.close()
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
        if "ADMIN" not in user["tg_id"][str(call.message.chat.id)]["roles"]:
            mail = requests.get('http://51.250.111.89:8080/api/appeals/user?answered=&find&type&district&topic&page&count',
                                headers={'Authorization': f'Rezh {user["tg_id"][str(call.message.chat.id)]["access_token"]}'})
            text = ''
            item_appeal = types.InlineKeyboardButton(text='Новое обращение', callback_data='new_appeal')
            if mail.text != '[]':
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
            else:
                text += 'Вы еще не отправили ни одного сообщения'
            keyboard.add(item_appeal)
        else:
            mail = requests.get('http://51.250.111.89:8080/api/appeals/admin',
                                headers={'Authorization': f'Rezh {user["tg_id"][str(call.message.chat.id)]["access_token"]}'})
            text = 'Сообщения, на которые еще никто не ответил' + '\n' * 2
            item_answer = types.InlineKeyboardButton(text='ответить на сообщение', callback_data='ans_appeal')
            for question in mail.json():
                if not question['response']:
                    text += f"Вопрос _{question['id']}_: *{question['text']}*" + '\n'
                    text += f"Тип: {question['type']}" + '\n'
                    text += f"От кого: {question['requester']['lastName']} {question['requester']['firstName']}" + '\n'
                    appeal_date = datetime.datetime.strptime(question['appealDate'], "%Y-%m-%dT%H:%M:%S.%f")
                    text += f"Дата: {appeal_date.strftime('%Y.%m.%d %H:%M:%S')}" + '\n' * 3
            keyboard.add(item_answer)
        item_back = types.InlineKeyboardButton(text='Вернуться', callback_data='lk')
        keyboard.add(item_back)
        bot.edit_message_text(message_id=call.message.message_id, chat_id=call.message.chat.id, text=text,
                              reply_markup=keyboard, parse_mode='Markdown')
        f.close()
    elif call.data == 'logout':
        k = types.InlineKeyboardMarkup(row_width=2)
        b = types.InlineKeyboardButton(text='Подтверждаю', callback_data='logout_del')
        b1 = types.InlineKeyboardButton(text='Случайно нажал', callback_data='lk')
        k.add(b, b1)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Хотите выйти?',
                              reply_markup=k)
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
        g.close()
        d.close()
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Вы успешно вышли', reply_markup=kb)
    elif call.data == 'ans_appeal':
        k = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        f = open('users.json', 'r', encoding='utf-8')
        user = json.loads(f.read())
        mail = requests.get('http://51.250.111.89:8080/api/appeals/admin',
                            headers={'Authorization': f'Rezh {user["tg_id"][str(call.message.chat.id)]["access_token"]}'})
        arr_id = [i['id'] for i in mail.json() if not i['response']]
        items = [types.KeyboardButton(text=i) for i in arr_id]
        k.add(*items)
        msg = bot.send_message(chat_id=call.message.chat.id, text='На какой вопрос вы хотите ответить?', reply_markup=k)
        bot.register_next_step_handler(msg, answer_appeal)
        f.close()
    elif call.data == 'new_appeal':
        k = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=3)
        k.row('Центр', 'Стройгородок', 'Машиностроителей')
        k.row('Гавань', "Вокзальный", "6-й участок")
        k.add('Все')
        msg = bot.send_message(chat_id=call.message.chat.id, text='Выберете район', reply_markup=k)
        bot.register_next_step_handler(msg, post_appeal_get_district)


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
                'id': user[1]['id'],
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
                                  text='Ваш аккаунт авторизирован в другом телеграмм аккаунте, пожалуйста выйдите, чтобы авторизироваться тут',
                                  reply_markup=kb)
        g.close()
    else:
        keyboard = types.InlineKeyboardMarkup()
        item = types.InlineKeyboardButton(text='Вернуться', callback_data='Yes')
        keyboard.add(item)
        bot.send_message(chat_id=message.chat.id, text='Неправльный ввод данных, попробуйте еще раз', reply_markup=keyboard)


def answer_appeal(message):
    id = message.text
    k = types.ReplyKeyboardRemove()
    msg = bot.send_message(chat_id=message.chat.id, text='Напишите ваш ответ на сообщение:', reply_markup=k)
    bot.register_next_step_handler(msg, patch_answer_appeal, id)


def patch_answer_appeal(message, id):
    k = types.InlineKeyboardMarkup()
    item_back = types.InlineKeyboardButton(text='Вернуться', callback_data='lk')
    k.add(item_back)
    f = open('users.json', 'r', encoding='utf-8')
    users = json.loads(f.read())
    form = {'id': (None, users['tg_id'][str(message.chat.id)]['id']), 'response': (None, message.text), 'frequent': (None, False)}
    requests.patch(url=f'http://51.250.111.89:8080/api/appeals/admin/{id}',
                   files=form, headers={'Authorization': f'Rezh {users["tg_id"][str(message.chat.id)]["access_token"]}'})
    user = requests.get(url=f'http://51.250.111.89:8080/api/appeals/admin/{id}',
                        headers={'Authorization': f'Rezh {users["tg_id"][str(message.chat.id)]["access_token"]}'})
    ping_user(user.json())
    bot.send_message(chat_id=message.chat.id, text='Ответ успешно отправлен', reply_markup=k)


def post_appeal_get_district(message):
    form = {'district': (None, message.text)}
    k = types.ReplyKeyboardMarkup(True, True, row_width=2)
    k.row('Обращение', "Предложение")
    k.row("Заявление", "Жалоба")
    msg = bot.send_message(chat_id=message.chat.id, text='Выберите тип сообщения:', reply_markup=k)
    bot.register_next_step_handler(msg, post_appeal_get_type, form)


def post_appeal_get_type(message, form):
    form['type'] = (None, message.text)
    k = types.ReplyKeyboardMarkup(True, True, row_width=2)
    k.row('Экономика и бюджет', "Социальные вопросы")
    k.row('Сельское хозяйство', "Местное самоуправление")
    k.row('Промышленность', "Строительство")
    k.row('Транспорт', "Связь")
    msg = bot.send_message(chat_id=message.chat.id, text='Выберите сферу деятельности', reply_markup=k)
    bot.register_next_step_handler(msg, post_appeal_get_topic, form)


def post_appeal_get_topic(message, form):
    form['topic'] = (None, message.text)
    k = types.ReplyKeyboardRemove()
    msg = bot.send_message(chat_id=message.chat.id, text='Напишите ваше сообщение:', reply_markup=k)
    bot.register_next_step_handler(msg, post_appeal_get_text, form)


def post_appeal_get_text(message, form):
    form['text'] = (None, message.text)
    text = ''
    text += f"Вопрос: _{form['text'][1]}_" + "\n" * 2
    text += f"Тип: _{form['type'][1]}_" + "\n"
    text += f"Район: _{form['district'][1]}_" + "\n"
    text += f"Сфера деятельности: _{form['topic'][1]}_"
    k = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    k.row('Написать еще раз', 'Отправить')
    msg = bot.send_message(chat_id=message.chat.id, text=text, reply_markup=k, parse_mode='Markdown')
    bot.register_next_step_handler(msg, post_appeal, form)


def post_appeal(message, form):
    k = types.InlineKeyboardMarkup()
    if message.text == 'Написать еще раз':
        item = types.InlineKeyboardButton(text='Отправить сообщение заново', callback_data='new_appeal')
        k.add(item)
        bot.send_message(text='Антека не была отправлена', chat_id=message.chat.id, reply_markup=k)
    elif message.text == 'Отправить':
        f = open('users.json', 'r', encoding='utf-8')
        users = json.loads(f.read())
        item = types.InlineKeyboardButton(text='Вернуться', callback_data='mail')
        k.add(item)
        requests.post(url='http://51.250.111.89:8080/api/appeals/user',
                      headers={'Authorization': f'Rezh {users["tg_id"][str(message.chat.id)]["access_token"]}'},
                      files=form)
        bot.send_message(text='Анкета была отправлена', chat_id=message.chat.id, reply_markup=k)


def ping_user(json_file):
    id = json_file['requester']['id']
    f = open('users.json', 'r', encoding='utf-8')
    users = json.loads(f.read())
    f.close()
    for i in users['tg_id'].keys():
        if users['tg_id'][i]['id'] == id:
            k = types.InlineKeyboardMarkup()
            item = types.InlineKeyboardButton('Перейти в сообщения', callback_data='mail')
            k.add(item)
            t = f'На ваш вопрос: _{json_file["text"]}_' + '\n' * 2
            t += 'Пришел ответ'
            bot.send_message(chat_id=i, text=t, reply_markup=k, parse_mode='Markdown')


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