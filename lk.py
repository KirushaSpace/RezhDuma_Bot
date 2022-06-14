import telebot
from config import TOKEN
from telebot import types
from list_msg import arr
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
        item_log = types.InlineKeyboardButton(text='Вход🔒', callback_data='login')
        markup.add(item_log)
    else:
        item_lk = types.InlineKeyboardButton(text='Личный кабинет💼', callback_data='lk')
        markup.add(item_lk)
    item_fq = types.InlineKeyboardButton(text='Часто задаваемые вопросы📄', callback_data='faq__0:3')
    item_site = types.InlineKeyboardButton(text='Переход на сайт🔍', url='http://rezh.ml/')
    markup.add(item_site, item_fq)
    bot.send_message(message.chat.id, f.read(), reply_markup=markup)
    f.close()
    g.close()


@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    if call.data == 'login':
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        item_log = types.InlineKeyboardButton(text='Ввести данные🔏', callback_data='Yes')
        item_reg = types.InlineKeyboardButton(text='Регистрация🔐', url='http://rezh.ml/registration')
        item_back = types.InlineKeyboardButton(text='<< Вернуться', callback_data='back')
        keyboard.add(item_log, item_reg, item_back)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Авторизация',
                              reply_markup=keyboard)
    elif call.data == 'lk':
        markup = types.InlineKeyboardMarkup(row_width=2)
        f = open('users.json', 'r', encoding='utf-8')
        users = json.loads(f.read())
        if 'ADMIN' in users['tg_id'][str(call.message.chat.id)]['roles']:
            item_mail = types.InlineKeyboardButton(text='Почта депутата✉️', callback_data='mail')
        else:
            item_mail = types.InlineKeyboardButton(text='Почта✉️', callback_data='mail')
        item_mes = types.InlineKeyboardButton(text='Сайт🔍', url='http://rezh.ml/')
        item_faq = types.InlineKeyboardButton(text='Часто задаваемые вопросы📄', callback_data='faq__0:3')
        item_back = types.InlineKeyboardButton(text='<< Вернуться', callback_data='back')
        item_logout = types.InlineKeyboardButton(text='Выйти из личного кабинета⚙️', callback_data='logout')
        markup.add(item_mail, item_mes, item_faq, item_back, item_logout)
        f = open('personalAccount.txt', 'r', encoding='utf-8')
        bot.edit_message_text(message_id=call.message.message_id, chat_id=call.message.chat.id,
                              text=f.read(), reply_markup=markup)
        f.close()
    elif call.data.startswith('faq'):
        s_faq = ''
        split_call = call.data.split('__')
        page = list(map(int, split_call[1].split(':')))
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        response = open('faq.json', 'r', encoding='utf-8')
        f = json.loads(response.read())
        response.close()
        if page[0] != 0:
            item_back = types.InlineKeyboardButton(text='⬅️Назад', callback_data=f'faq__{page[0]-3}:{page[1]-3}')
            keyboard.add(item_back)
        if page[1] < len(f):
            item_next = types.InlineKeyboardButton(text='Дальше ➡️', callback_data=f'faq__{page[0]+3}:{page[1]+3}')
            keyboard.add(item_next)
        else:
            page[1] = len(f)
        item_remove = types.InlineKeyboardButton(text='<< Вернуться', callback_data='back')
        keyboard.add(item_remove)
        for i in range(page[0], page[1]):
            s_faq += f"Вопрос: *{f[i]['text']}*" + '\n'
            s_faq += f"Тип: {f[i]['type']}" + '\n'
            appeal_date = datetime.datetime.strptime(f[i]['appealDate'], "%Y-%m-%dT%H:%M:%S.%f")
            s_faq += f"Дата: {appeal_date.strftime('%Y.%m.%d %H:%M:%S')}" + '\n'
            s_faq += f"_Ответ: {f[i]['response']}_" + '\n'
            s_faq += f"_От кого: {f[i]['responsibleName']}_" + '\n'
            response_date = datetime.datetime.strptime(f[i]['responseDate'], "%Y-%m-%dT%H:%M:%S.%f")
            s_faq += f"_Дата: {response_date.strftime('%Y.%m.%d %H:%M:%S')}_" + '\n' * 3
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=s_faq,
                              parse_mode='Markdown', reply_markup=keyboard)
        response.close()
    elif call.data == 'back':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        start(call.message)
    elif call.data == 'Yes':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        msg = bot.send_message(chat_id=call.message.chat.id, text='Введите логин (почту) к личному кабинету')
        bot.register_next_step_handler(msg, user_login)
    elif call.data.startswith('mail'):
        f = open('users.json', 'r', encoding='utf-8')
        user = json.loads(f.read())
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        if "ADMIN" not in user["tg_id"][str(call.message.chat.id)]["roles"]:
            mail = requests.get('http://51.250.111.89:8080/api/appeals/user?answered=&find&type&district&topic&page&count',
                                headers={'Authorization': f'Rezh {user["tg_id"][str(call.message.chat.id)]["access_token"]}'})
            text = ''
            item_appeal = types.InlineKeyboardButton(text='Новое обращение📩', callback_data='new_appeal')
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
        item_back = types.InlineKeyboardButton(text='<< Вернуться', callback_data='lk')
        keyboard.add(item_back)
        bot.edit_message_text(message_id=call.message.message_id, chat_id=call.message.chat.id, text=text,
                              reply_markup=keyboard, parse_mode='Markdown')
        f.close()
    elif call.data == 'logout':
        k = types.InlineKeyboardMarkup(row_width=2)
        b = types.InlineKeyboardButton(text='Подтверждаю', callback_data='logout_del')
        b1 = types.InlineKeyboardButton(text='<< Случайно нажал', callback_data='lk')
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
        item_back = types.InlineKeyboardButton(text='<< Вернуться', callback_data='back')
        kb.add(item_back)
        g.close()
        d.close()
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Вы успешно вышли',
                              reply_markup=kb)
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
        k = types.InlineKeyboardMarkup(row_width=3)
        k.row(types.InlineKeyboardButton(text='Центр', callback_data='district Цр'),
              types.InlineKeyboardButton(text='Стройгородок', callback_data='district Ск'),
              types.InlineKeyboardButton(text='Машиностроителей', callback_data='district Мй'))
        k.row(types.InlineKeyboardButton(text='Гавань', callback_data='district Гь'),
              types.InlineKeyboardButton(text='Вокзальный', callback_data='district Вй'),
              types.InlineKeyboardButton(text='6-й участок', callback_data='district 6к'))
        k.row(types.InlineKeyboardButton(text='Все', callback_data='district Все'))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Выберете район', reply_markup=k)
    elif call.data.startswith('district'):
        ans = call.data.split()
        k = types.InlineKeyboardMarkup(row_width=2)
        k.row(types.InlineKeyboardButton(text='Обращение', callback_data=f'type {ans[1]},Ое'),
              types.InlineKeyboardButton(text='Предложение', callback_data=f'type {ans[1]},Пе'))
        k.row(types.InlineKeyboardButton(text='Заявление', callback_data=f'type {ans[1]},Зе'),
              types.InlineKeyboardButton(text='Жалоба', callback_data=f'type {ans[1]},Жа'))
        k.row(types.InlineKeyboardButton(text='Все', callback_data=f'type {ans[1]},Все'))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Выберите тип сообщения', reply_markup=k)
    elif call.data.startswith('type'):
        ans = call.data.split()
        k = types.InlineKeyboardMarkup(row_width=2)
        k.row(types.InlineKeyboardButton(text='Экономика и бюджет', callback_data=f'topic {ans[1]},Эт'),
              types.InlineKeyboardButton(text='Социальные вопросы', callback_data=f'topic {ans[1]},Сы'),
              types.InlineKeyboardButton(text='Сельское хозяйство', callback_data=f'topic {ans[1]},Сео'))
        k.row(types.InlineKeyboardButton(text='Местное самоуправление', callback_data=f'topic {ans[1]},Ме'),
              types.InlineKeyboardButton(text='Промышленность', callback_data=f'topic {ans[1]},Пь'),
              types.InlineKeyboardButton(text='Строительство', callback_data=f'topic {ans[1]},Сто'))
        k.row(types.InlineKeyboardButton(text='Транспорт', callback_data=f'topic {ans[1]},Тт'),
              types.InlineKeyboardButton(text='Связь', callback_data=f'topic {ans[1]},Сь'))
        k.row(types.InlineKeyboardButton(text='Все', callback_data=f'topic {ans[1]},Все'))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Выберите сферу деятельности', reply_markup=k)
    elif call.data.startswith('topic'):
        ans = call.data.split()[1]
        out = ans.split(',')
        form = {'district': (None, arr[out[0]]), 'type': (None, arr[out[1]]), 'topic': (None, arr[out[2]])}
        msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text='Введите сообщение')
        bot.register_next_step_handler(msg, post_appeal_get_text, form)


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
            bot.send_message(message.chat.id, f"Успешный вход в систему🔓! Добро пожаловать, {user[1]['firstName']} {user[1]['lastName']}")
            markup = types.InlineKeyboardMarkup()
            item_lk = types.InlineKeyboardButton(text='Переход в личный кабинет💼', callback_data='lk')
            markup.add(item_lk)
            bot.send_message(message.chat.id, 'переход', reply_markup=markup)
            users.close()
        else:
            kb = types.InlineKeyboardMarkup()
            item = types.InlineKeyboardButton(text='<< Вернуться', callback_data='Yes')
            kb.add(item)
            bot.send_message(chat_id=message.chat.id,
                             text='Ваш аккаунт авторизирован в другом телеграмм аккаунте, пожалуйста выйдите, чтобы авторизироваться тут',
                             reply_markup=kb)
        g.close()
    else:
        keyboard = types.InlineKeyboardMarkup()
        item = types.InlineKeyboardButton(text='<< Вернуться', callback_data='Yes')
        keyboard.add(item)
        bot.send_message(chat_id=message.chat.id, text='Неправльный ввод данных, попробуйте еще раз',
                         reply_markup=keyboard)


def answer_appeal(message):
    id = message.text
    k = types.ReplyKeyboardRemove()
    msg = bot.send_message(chat_id=message.chat.id, text='Напишите ваш ответ на сообщение:', reply_markup=k)
    bot.register_next_step_handler(msg, patch_answer_appeal, id)


def patch_answer_appeal(message, id):
    k = types.InlineKeyboardMarkup()
    item_back = types.InlineKeyboardButton(text='<< Вернуться', callback_data='lk')
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
        item_back = types.InlineKeyboardButton(text='<< Вернуться', callback_data='lk')
        k.add(item)
        bot.send_message(text='Анкета не была отправлена', chat_id=message.chat.id, reply_markup=k)
    elif message.text == 'Отправить':
        f = open('users.json', 'r', encoding='utf-8')
        users = json.loads(f.read())
        item = types.InlineKeyboardButton(text='<< Вернуться', callback_data=f'mail все,все,все')
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


bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()
bot.polling(none_stop=True)