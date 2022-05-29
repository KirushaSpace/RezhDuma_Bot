import telebot
from config import TOKEN
from telebot import types

bot = telebot.TeleBot(TOKEN)
user_forms = [['gg', 'fff']]
user_form = [0] * 2


@bot.message_handler(commands=['start'])
def start(message):
    f = open('start_message.txt', 'r', encoding='utf-8')
    global user_forms
    markup = types.InlineKeyboardMarkup(row_width=1)
    item_log = types.InlineKeyboardButton(text='Вход', callback_data='login')
    markup.add(item_log)
    if message.from_user.id in user_forms:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=f.read())
        item_lk = types.InlineKeyboardButton(text='Личный кабинет', callback_data='lk')
        markup.add(item_lk)

    item_faq = types.InlineKeyboardButton(text='Часто задаваемые вопросы', callback_data='faq')
    item_site = types.InlineKeyboardButton(text='Переход на сайт', url='https://www.youtube.com/watch?v=dQw4w9WgXcQ')
    markup.add(item_site, item_faq)


    bot.send_message(message.chat.id, f.read(), reply_markup=markup)
    f.close()


@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    if call.data == 'login':
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        item_log = types.InlineKeyboardButton(text='Ввести данные', callback_data='Yes')
        item_reg = types.InlineKeyboardButton(text='Не зарегистрирован?', url='https://www.youtube.com/watch?v=dQw4w9WgXcQ')
        item_back = types.InlineKeyboardButton(text='Вернуться', callback_data='back')
        keyboard.add(item_log, item_reg, item_back)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Авторизация', reply_markup=keyboard)
    elif call.data == 'lk':
        markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
        item_mail = types.KeyboardButton(text='Почта')
        item_mes = types.KeyboardButton(text='заявки')
        markup.add(item_mail, item_mes)
        bot.send_message(call.message.chat.id, 'Выберете куда вы хотите перейти', reply_markup=markup)
    elif call.data == 'faq':
        bot.send_message(call.message.chat.id, 'Пока часто задаваемых вопросов нет')
    elif call.data == 'back':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        start(call.message)
    elif call.data == 'Yes':
        msg = bot.send_message(chat_id=call.message.chat.id, text='Введите логин (почту) к личному кабинету')
        bot.register_next_step_handler(msg, user_login)


def user_login(message):
    global user_form, user_forms
    login = message.text
    # todo сделать обработчик логина
    user_form = [0] * 2
    user_form[0] = login
    msg = bot.send_message(message.chat.id, 'Введите пароль:')
    bot.register_next_step_handler(msg, user_password)


def user_password(message):
    global user_form, user_forms
    password = message.text
    user_form[1] = password
    # if user_form in user_forms:
    user_forms.append(message.from_user.id)
    # todo обработчик пароля
    # todo проверка есть ли пользователь в системе
    bot.send_message(message.chat.id, 'Проверяю...')
    bot.send_message(message.chat.id, 'Успешный вход в систему, добро пожаловать, {Имя} {Фамилия}')
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='Вернуться', callback_data='back')
    markup.add(button)
    bot.send_message(message.chat.id, 'вернитесь в начало', reply_markup=markup)
    # else:
    #     keyboard = types.InlineKeyboardMarkup()
    #     item = types.InlineKeyboardButton(text='Вернуться', callback_data='Yes')
    #     keyboard.add(item)
    #     bot.send_message(chat_id=message.chat.id, text='Неправльный ввод данных, попробуйте еще раз', reply_markup=keyboard)


@bot.message_handler(commands=['help'])
def help(message):
    cmds = open('help.txt', 'r', encoding="utf-8")
    bot.send_message(message.chat.id, cmds.read())


@bot.message_handler(commands=['persons'])
def per(message):
    global user_forms
    bot.send_message(message.chat.id, '\n'.join(user_forms))


@bot.message_handler(commands=['info'])
def information(message):
    bot.send_message(message.chat.id, message)


@bot.message_handler(content_types=["text"])
def any_msg(message):
    bot.send_message(message.chat.id, "обработчик текста")


bot.polling(none_stop=True)