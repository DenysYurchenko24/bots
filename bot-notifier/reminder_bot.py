#!/usr/bin/python3
import telebot
from telebot import types

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
import telebot_calendar
from telebot_calendar import CallbackData
import calendar
import typing
import datetime
import time

import locale
import random
import string
import threading
from apscheduler.schedulers.background import BackgroundScheduler

import config


bot = telebot.TeleBot(config.TOKEN)
print(bot.get_me())

now = datetime.datetime.now()
locale.setlocale(locale.LC_ALL, "ru_RU")
calendar_1 = CallbackData("calendar_1", "action", "year", "month", "day")
my_calend = telebot_calendar.create_calendar(
    name=calendar_1.prefix,
    year=now.year,
    month=now.month)

temp_date = {}  # Временная дата после выбора на календаре (ожидает подтверждения) с привязкой к ид юзера
for_reminder = {}  # Итоговый словарь с данными обо всех датах и текстах напоминаний всех юзеров
once_or_periodic = {}  # Одноразовая (1) или регулярная (2) проверка с привязкой к ид юзера
text_or_time = {}  # Указывает декоратору-обработчику вводимого текста, обрабатывать его как интервал или
# как текст-напоминание (с привязкой к ид юзера)
latest_time = {}  # Выбранное время (дата, интервал) до введения текста-напоминания (временный контейнер)
# с привязкой к ид юзера
key_to_edit = {}  # Словарь с ключами - ид юзеров и значениями - ключами словаря for_reminder для конкретного юзера,
# которым нужно присвоить новые значения (новый текст напоминания)


@bot.message_handler(commands=['help'])
def helper(message):
    bot.send_message(message.from_user.id,
                     'Как пользоваться ботом? <b>Очень просто!</b>' + '\n' * 2 + 'Ты выбираешь дату, день недели или '
                     'временной интервал напоминания, а затем указываешь текст, который хочешь получить в сообщении от '
                     'бота в указанное время.Текст напоминания затем можно отредактировать, а напоминание - удалить '
                     '(просто воспользуйся командой /manage).' + '\n' * 2 + 'Ты можешь выбрать из 5 возможных вариантов'
                     ':' + '\n' + '1. Одноразовое напоминание в определенную дату.' + '\n' + '2.Одноразовое напоминание'
                     ' через заданный вручную интервал в часах, минутах или секундах.' + '\n' + '3. Периодическое '
                     'напоминание по определенным числам месяца.' + '\n' + '4. Периодическое напоминание по дням недели'
                     '.' + '\n' + '5. Периодическое напоминание с заданным вручную интервалом в часах, минутах или '
                     'секундах.' + '\n' + 'Уведомления, запланированные на дни недели или месяца, придут в 9 часов '
                     'утра соответствующего дня. К сожалению, пока нет возможности добавлять несколько отдельных '
                     'напоминаний одного типа на одну и ту же дату или день недели. Т.е. на одну дату можно одновременно'
                     ' поставить одноразовое и периодическое напоминание, но нельзя поставить более одного одноразового'
                     ' или одного периодического (как и на один день недели нельзя поставить более одного периодического'
                     ' напоминания). В следующих версиях эти возможности будут добавлены вместе с функцией выбора точного'
                     ' времени получения напоминания и количества сообщений с одним напоминанием.' + '\n' * 2 +
                     'Все это работает примерно вот так:', parse_mode='HTML')
    bot.send_video(message.from_user.id, 'BAACAgIAAxkBAAITJF5SeFwgtCkSIKZ7YVcaqfc4gX1OAAJrBgACx2aQSh16RI5xsj7FGAQ')


keyboard1 = types.InlineKeyboardMarkup(row_width=1)
once = types.InlineKeyboardButton('Одноразовое напоминание', callback_data='once')
periodic = types.InlineKeyboardButton('Периодическое напоминание', callback_data='periodic')
keyboard1.add(once, periodic)

keyboard2 = types.InlineKeyboardMarkup(row_width=2)
on_days = types.InlineKeyboardButton('По заданным дням', callback_data='on_days')
intervals = types.InlineKeyboardButton('С заданным интервалом', callback_data='intervals')
back_to_k1 = types.InlineKeyboardButton('<<Назад', callback_data='back_to_k1')
keyboard2.add(on_days, intervals, back_to_k1)

keyboard3 = types.InlineKeyboardMarkup(row_width=2)
on_numbers = types.InlineKeyboardButton('По числам', callback_data='on_numbers')
days_of_week = types.InlineKeyboardButton('По дням недели', callback_data='days_of_week')
back_to_k2 = types.InlineKeyboardButton('<<Назад', callback_data='back_to_k2')
keyboard3.add(on_numbers, days_of_week, back_to_k2)

keyboard4 = types.InlineKeyboardMarkup(row_width=7)
monday = types.InlineKeyboardButton('Пн', callback_data='monday')
tuesday = types.InlineKeyboardButton('Вт', callback_data='tuesday')
wednesday = types.InlineKeyboardButton('Ср', callback_data='wednesday')
thursday = types.InlineKeyboardButton('Чт', callback_data='thursday')
friday = types.InlineKeyboardButton('Пт', callback_data='friday')
saturday = types.InlineKeyboardButton('Сб', callback_data='saturday')
sunday = types.InlineKeyboardButton('Вс', callback_data='sunday')
back_to_k3 = types.InlineKeyboardButton('<<Назад', callback_data='back_to_k3')
keyboard4.add(monday, tuesday, wednesday, thursday, friday, saturday, sunday, back_to_k3)

keyboard5 = types.InlineKeyboardMarkup()
yes = types.InlineKeyboardButton('Да!', callback_data='yes')
no = types.InlineKeyboardButton('Нет, погодите-ка...', callback_data='no')
keyboard5.row(yes, no)

keyboard6 = types.InlineKeyboardMarkup(row_width=2)
on_cal = types.InlineKeyboardButton('Дай мне календарь!', callback_data='on_cal')
timer = types.InlineKeyboardButton('Введу вручную', callback_data='timer')
back_to_k1 = types.InlineKeyboardButton('<<Назад', callback_data='back_to_k1')
keyboard6.add(on_cal, timer, back_to_k1)

keyboard7 = types.InlineKeyboardMarkup(row_width=1)
once = types.InlineKeyboardButton('Добавить одноразовое напоминание', callback_data='once')
periodic = types.InlineKeyboardButton('Добавить периодическое напоминание', callback_data='periodic')
edit = types.InlineKeyboardButton('Редактировать текст напоминания', callback_data='edit')
delete = types.InlineKeyboardButton('Удалить напоминание', callback_data='delete')
keyboard7.add(once, periodic, edit, delete)


@bot.message_handler(commands=['start'])
def start(message):
    for_reminder[int(message.from_user.id)] = dict()  # добавили ид пользователя {id: {}}
    once_or_periodic[int(message.from_user.id)] = list()
    text_or_time[int(message.from_user.id)] = ''
    bot.send_message(message.from_user.id, 'Привет!' + '\n' * 2 +
                     'Я твой бот-напоминалка. Буду следить, чтобы ты не забыл(а) поздравить родственников с днем '
                     'рождения, купить продукты, спасти мир и забрать ребенка из садика.' + '\n' * 2 + 'Если нужно '
                     'будет удалить или добавить напоминание, ты в любой момент можешь воспользоваться командой '
                     '/manage.' + '\n' * 2 + 'Чтобы ознакомиться с подробной инструкцией по работе с ботом, '
                     'воспользуйся командой /help, либо выбери раздел "Помощь" в выпадающем меню справа вверху ("Помощь'
                     ' с ботом" для десктопных версий).')
    print(message.from_user.id)
    bot.send_message(message.from_user.id, 'Выбери, что тебе нужно:', reply_markup=keyboard1)
  


@bot.message_handler(commands=['restart'])
def restart(message):
    for_reminder[int(message.from_user.id)] = dict()
    once_or_periodic[int(message.from_user.id)] = list()
    bot.send_message(message.from_user.id, 'Снова здравствуй! Выбери, что тебе нужно:', reply_markup=keyboard1)



@bot.message_handler(commands=['manage'])
def my_reminders(message):
    if for_reminder[message.from_user.id] == {}:
        bot.send_message(message.from_user.id, 'У тебя пока нет напоминаний')
        bot.send_message(message.from_user.id, 'Выбери, что тебе нужно:', reply_markup=keyboard1)
    else:
        s = str()
        temp = [k for k, v in for_reminder[message.from_user.id].items()]
        i = 1
        for k, v in for_reminder[message.from_user.id].items():
            if k == 'friday':
                key = 'По пятницам'
            elif k == 'monday':
                key = 'По понедельникам'
            elif k == 'tuesday':
                key = 'По вторникам'
            elif k == 'wednesday':
                key = 'По средам'
            elif k == 'thursday':
                key = 'По четвергам'
            elif k == 'saturday':
                key = 'По субботам'
            elif k == 'sunday':
                key = 'По воскресеньям'
            elif once_or_periodic[message.from_user.id][temp.index(k)] == 2 and k.isdigit():
                key = f'По {k}-м числам'
            elif once_or_periodic[message.from_user.id][temp.index(k)] == 2 and not k.replace(' ', '').isdigit():
                key = f'Каждые {k}'
            elif once_or_periodic[message.from_user.id][temp.index(k)] == 1 and k.replace(' ', '').isdigit():
                key = k.replace(' ', '.')
            else:
                key = str(k).capitalize()
            s += (f'{str(i)}) <b>{key}:</b> {str(v)}' + '\n')
            i += 1
        bot.send_message(message.from_user.id, 'Вот твои напоминания:' + '\n' * 2 + s, parse_mode='HTML')
        bot.send_message(message.from_user.id, 'Что ты хочешь сделать?', reply_markup=keyboard7)


@bot.message_handler(content_types=['text'])
def texter(message):
    if text_or_time[message.from_user.id] == 'text':
        text_handle(message)
    elif text_or_time[message.from_user.id] == 'time':
        reply_handle_for_time(message)
    else:
        a = 'Я тебя не понимаю... Воспользуйся встроенными командами.'
        b = 'Прости, но тебе придется воспользоваться встроенными командами...'
        c = [a, b]
        bot.send_message(message.from_user.id, random.choice(c))


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_1.prefix))
def callback_inline(call: CallbackQuery):
    name, action, year, month, day = call.data.split(calendar_1.sep)
    date = telebot_calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
    )
    if action == "DAY":
        if date.strftime('%Y.%m.%d') < time.strftime('%Y.%m.%d'):
            bot.send_message(call.from_user.id,
                             'Похоже, ты выбрал(a) дату из прошлого. Это бот для напоминаний, а не машина времени!',
                             reply_markup=my_calend)
        else:
            if date.strftime('%B').startswith('мар') or date.strftime('%B').startswith('авг'):
                to_pr = date.strftime('%B') + 'а'
                to_print = date.strftime('%d ') + to_pr + date.strftime(' %Y')
            else:
                to_pr = date.strftime('%B')[:-1] + 'я'
                to_print = date.strftime('%d ') + to_pr + date.strftime(' %Y')
            bot.send_message(call.from_user.id, f"Ты выбрал(а): <b>{to_print}</b>, это правильная дата?",
                             reply_markup=keyboard5, parse_mode='HTML')
            if once_or_periodic[call.from_user.id][-1] == 1:
                temp_date.update({int(call.from_user.id): str(date.strftime('%d %m %Y'))})
            elif once_or_periodic[call.from_user.id][-1] == 2:
                temp_date.update({int(call.from_user.id): str(date.strftime('%d'))})
    elif action == "BACK":
        if once_or_periodic[call.from_user.id][-1] == 1:
            bot.send_message(call.from_user.id, 'Хочешь выбрать дату на календаре или поставить таймер?',
                             reply_markup=keyboard6)
        elif once_or_periodic[call.from_user.id][-1] == 2:
            bot.send_message(call.from_user.id, 'Ориентируемся по числам или по дням недели?', reply_markup=keyboard3)


@bot.callback_query_handler(func=lambda call: True)
def callback_keyboard(call):
    if call.data == 'once':
        once_or_periodic[int(call.from_user.id)].append(1)
        print(once_or_periodic)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.from_user.id, 'Хочешь выбрать дату на календаре или поставить таймер?',
                         reply_markup=keyboard6)
    elif call.data == 'periodic':
        once_or_periodic[int(call.from_user.id)].append(2)
        print(once_or_periodic)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.from_user.id, 'Хочешь получать напоминания по определенным дням или, может, '
                                            'через одинаковый промежуток времени?', reply_markup=keyboard2)
    elif call.data == 'on_days':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.from_user.id, 'Ориентируемся по числам или по дням недели?', reply_markup=keyboard3)
    elif call.data == 'intervals':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.from_user.id, 'Введи интервал напоминания (например, "40 секунд" или "15 минут"): ')
        text_or_time.update({int(call.from_user.id): 'time'})
    elif call.data == 'on_numbers':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.from_user.id, 'Выбирай дату:', reply_markup=my_calend)
    elif call.data == 'days_of_week':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.from_user.id, 'Выбирай день недели:', reply_markup=keyboard4)
    elif call.data in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        for_reminder[call.from_user.id].update({call.data: ''})  # {id: {monday : 'textsample'}}
        print(for_reminder)
        latest_time.update({call.from_user.id: call.data})
        bot.send_message(call.from_user.id, 'Теперь введи текст, который ты хочешь получать: ')
        text_or_time.update({int(call.from_user.id): 'text'})
    elif call.data == 'yes':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        for k, v in temp_date.items():
            if k == call.from_user.id:
                for_reminder[call.from_user.id].update({v: ''})  # {id: {01 01 2020/01: 'textsample'}}
                latest_time.update({call.from_user.id: v})
        print(for_reminder)
        bot.send_message(call.from_user.id, 'Отлично! Теперь введи текст, который ты хочешь получить: ')
        text_or_time.update({int(call.from_user.id): 'text'})
    elif call.data == 'no':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.from_user.id, 'Возвращаю календарь', reply_markup=my_calend)
    elif call.data == 'on_cal':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.from_user.id, "Выбирай дату!", reply_markup=my_calend)
    elif call.data == 'timer':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.from_user.id, 'Введи значение таймера (напр. "Через 1 час" или "Через 33 минуты":)')
        text_or_time.update({int(call.from_user.id): 'time'})
    elif call.data == 'delete':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        numbers = [str(i + 1) + 'd' for i in range(0, len(for_reminder[call.from_user.id]))]
        keyboard8 = types.InlineKeyboardMarkup(row_width=5)
        keyboard8.add(*[types.InlineKeyboardButton(number[0:-1], callback_data=number) for number in numbers])
        keyboard8.add(types.InlineKeyboardButton('<<Назад', callback_data='back_to_k7'))
        bot.send_message(call.from_user.id, 'Какое напоминание нужно удалить?', reply_markup=keyboard8)
    elif call.data in [str(i + 1) + 'd' for i in range(0, len(for_reminder[call.from_user.id]))]:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        lst = [i for i in enumerate(for_reminder[call.from_user.id])]
        for i in lst:
            if i[0] == int(call.data[0:-1]) - 1:
                tem = [k for k, v in for_reminder[call.from_user.id].items()]
                del once_or_periodic[call.from_user.id][tem.index(i[1])]
                for_reminder[call.from_user.id].pop(i[1])
        bot.send_message(call.from_user.id, 'Напоминание было успешно удалено. Проверить список напоминаний можно '
                                            'командой /manage')
    elif call.data == 'edit':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        numbers = [str(i + 1) + 'e' for i in range(0, len(for_reminder[call.from_user.id]))]
        keyboard9 = types.InlineKeyboardMarkup(row_width=5)
        keyboard9.add(*[types.InlineKeyboardButton(number[0:-1], callback_data=number) for number in numbers])
        keyboard9.add(types.InlineKeyboardButton('<<Назад', callback_data='back_to_k7'))
        bot.send_message(call.from_user.id, 'Какое напоминание нужно отредактировать?', reply_markup=keyboard9)
    elif call.data in [str(i + 1) + 'e' for i in range(0, len(for_reminder[call.from_user.id]))]:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        lst = [i for i in enumerate(for_reminder[call.from_user.id])]
        for i in lst:
            if i[0] == int(call.data[0:-1]) - 1:
                text_or_time.update({int(call.from_user.id): 'text'})
                key_to_edit[call.from_user.id] = i[1]
                bot.send_message(call.from_user.id, 'Введи новый текст напоминания:')
    elif call.data == 'back_to_k1':  # или к клаве 7, если напоминания уже есть
        if for_reminder[call.from_user.id] == {}:
            del once_or_periodic[call.from_user.id][-1]
            print(once_or_periodic)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.from_user.id, 'Выбери, что тебе нужно:', reply_markup=keyboard1)
        else:
            del once_or_periodic[call.from_user.id][-1]
            print(once_or_periodic)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.from_user.id, 'Что ты хочешь сделать?', reply_markup=keyboard7)
    elif call.data == 'back_to_k2':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.from_user.id, 'Хочешь получать напоминания по определенным дням или, может, '
                                            'через одинаковый промежуток времени?', reply_markup=keyboard2)
    elif call.data == 'back_to_k3':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.from_user.id, 'Ориентируемся по числам или по дням недели?', reply_markup=keyboard3)
    elif call.data == 'back_to_k7':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.from_user.id, 'Что ты хочешь сделать?', reply_markup=keyboard7)


def reply_handle_for_time(message):
    a = message.text.lower().split()
    if (once_or_periodic[message.from_user.id][-1] == 2 and (not a[-1].startswith('сек') and not a[-1].startswith('мин')
            and not a[-1].startswith('час'))) or ((once_or_periodic[message.from_user.id][-1] == 1 and len(a) != 3) or (
            once_or_periodic[message.from_user.id][-1] == 2 and len(a) != 2)) or (
            once_or_periodic[message.from_user.id][-1] == 1 and (
            not a[-1].startswith('сек') and not a[-1].startswith('мин') and not a[-1].startswith('час'))):
        bot.send_message(message.from_user.id, 'Пожалуйста, введи интервал в корректном формате')
    else:
        for_reminder[message.from_user.id].update({message.text.lower(): ''})  # {id: {через 1 час: ''}}
        print(for_reminder)
        latest_time.update({message.from_user.id: message.text.lower()})
        bot.send_message(message.from_user.id, 'Отлично! Теперь введи текст, который ты хочешь получить:')
        text_or_time.update({int(message.from_user.id): 'text'})


def text_handle(message):
    if message.from_user.id in key_to_edit:
        for_reminder[message.from_user.id][key_to_edit[message.from_user.id]] = message.text
        key_to_edit.pop(message.from_user.id)
        bot.send_message(message.from_user.id, 'Напоминание было успешно отредактировано. '
                                               'Проверить список напоминаний можно командой /manage')
        text_or_time[message.from_user.id] = ''
    else:
        for_reminder[message.from_user.id].update({latest_time[message.from_user.id]: message.text})
        # {id: {через 1 час: сделать что-то}}
        print(for_reminder)
        text_or_time[message.from_user.id] = ''
        reminder(message)


def reminder(message):
    a = []
    for k, v in for_reminder[message.from_user.id].items():
        a.append(k)
        a.append(v)
    if once_or_periodic[message.from_user.id][-1] == 1:
        if a[-2].replace(' ', '').isdigit():
            key = a[-2].replace(' ', '.')
            bot.send_message(message.from_user.id,
                             f'Готово! <b>{key}</b> в 9:00 я пришлю одноразовое напоминание с таким текстом: '
                             + a[-1] + '\n' * 2 + 'Проверить напоминания можно командой /manage', parse_mode='HTML')
        else:
            key = a[-2].capitalize()
            bot.send_message(message.from_user.id,
                             f'Готово! <b>{key}</b> я пришлю одноразовое напоминание с таким текстом: '
                             + a[-1] + '\n' * 2 + 'Проверить напоминания можно командой /manage', parse_mode='HTML')
    elif once_or_periodic[message.from_user.id][-1] == 2:
        if a[-2] == 'friday':
            key = 'По пятницам'
        elif a[-2] == 'monday':
            key = 'По понедельникам'
        elif a[-2] == 'tuesday':
            key = 'По вторникам'
        elif a[-2] == 'wednesday':
            key = 'По средам'
        elif a[-2] == 'thursday':
            key = 'По четвергам'
        elif a[-2] == 'saturday':
            key = 'По субботам'
        elif a[-2] == 'sunday':
            key = 'По воскресеньям'
        elif a[-2].isdigit():
            key = f'По {a[-2]}-м числам'
        elif not a[-2].replace(' ', '').isdigit():
            key = f'Каждые {a[-2]}'
        if key != f'Каждые {a[-2]}':
            bot.send_message(message.from_user.id,
                             f'Готово! <b>{key}</b> в 9:00 я буду присылать напоминания с таким текстом: '
                             + a[-1] + '\n' * 2 + 'Проверить напоминания можно командой /manage', parse_mode='HTML')
        else:
            bot.send_message(message.from_user.id,
                             f'Готово! <b>{key}</b> я буду присылать напоминания с таким текстом: '
                             + a[-1] + '\n' * 2 + 'Проверить напоминания можно командой /manage', parse_mode='HTML')
    for_thread = ''.join(random.choices(string.ascii_lowercase, k=6))
    form = 'thread1 = threading.Thread(target=scheduler, args=[message, ])'
    form1 = 'thread1.start()'
    form = form.replace('thread1', for_thread)
    form1 = form1.replace('thread1', for_thread)
    exec(form)
    exec(form1)


def scheduler(message):
    a = [k for k, v in for_reminder[message.from_user.id].items()]
    times = str(a[-1]).split()
    if once_or_periodic[message.from_user.id][-1] == 1:
        if times[0].startswith('через'):  # обработка для интервала одноразовой проверки
            if times[2].startswith('сек'):
                num = float(times[1])
            elif times[2].startswith('мин'):
                num = float(times[1]) * 60
            elif times[2].startswith('час'):
                num = float(times[1]) * 3600
            while a[-1] in for_reminder[message.from_user.id]:
                time.sleep(num)
                task = 'Твое напоминание подъехало!' + '\n' * 2 + str(for_reminder[message.from_user.id][a[-1]] +
                        '\n' * 2 + 'Проверить список напоминаний можно командой /manage')
                bot.send_message(message.from_user.id, task)
                tem = [k for k, v in for_reminder[message.from_user.id].items()]
                del once_or_periodic[message.from_user.id][tem.index(a[-1])]
                for_reminder[message.from_user.id].pop(a[-1])
                return
        else:  # обработка для одноразового календаря
            sched = BackgroundScheduler()

            def my_job():
                task = 'Твое напоминание подъехало!' + '\n' * 2 + str(for_reminder[message.from_user.id][a[-1]] +
                        '\n' * 2 + 'Проверить список напоминаний можно командой /manage')
                bot.send_message(message.from_user.id, task)
                tem = [k for k, v in for_reminder[message.from_user.id].items()]
                del once_or_periodic[message.from_user.id][tem.index(a[-1])]
                for_reminder[message.from_user.id].pop(a[-1])
            job = sched.add_job(my_job, 'cron', day=int(times[0]), month=int(times[1]), year=int(times[2]),
                                hour=7, minute=0, replace_existing=True)  # в 9 часов утра (+2 часа) из-за сервера
            sched.start()
            while a[-1] in for_reminder[message.from_user.id]:
                continue
            else:
                try:
                    job.remove()
                except Exception as e:
                    print(e)
                return
    else:
        if len(times) == 1 and not times[0].isdigit():
            # обработка для регулярной проверки по дням недели (friday)
            sched = BackgroundScheduler()

            def my_job():
                task = 'Твое напоминание подъехало!' + '\n' * 2 + str(for_reminder[message.from_user.id][a[-1]] +
                                                    '\n' * 2 + 'Проверить список напоминаний можно командой /manage')
                bot.send_message(message.from_user.id, task)
            job = sched.add_job(my_job, 'cron', day_of_week=times[0][0:3], hour=7, minute=0, replace_existing=True)
            sched.start()  # в 9 часов утра (+2 часа) из-за сервера
            while a[-1] in for_reminder[message.from_user.id]:
                continue
            else:
                job.remove()
                return
        elif len(times) == 2:
            if times[1].startswith('сек'):
                num = float(times[0])
            elif times[1].startswith('мин'):
                num = float(times[0]) * 60
            elif times[1].startswith('час'):
                num = float(times[0]) * 360
            while a[-1] in for_reminder[message.from_user.id]:
                task = 'Твое напоминание подъехало!' + '\n' * 2 + str(for_reminder[message.from_user.id][a[-1]] +
                                                    '\n' * 2 + 'Проверить список напоминаний можно командой /manage')
                bot.send_message(message.from_user.id, task)
                time.sleep(num)
            else:
                return
        elif len(times) == 1 and times[0].isdigit():
            # обработка для регулярной проверки по дням месяца (20 числа)
            sched = BackgroundScheduler()

            def my_job():
                task = 'Твое напоминание подъехало!' + '\n' * 2 + str(for_reminder[message.from_user.id][a[-1]] +
                                                    '\n' * 2 + 'Проверить список напоминаний можно командой /manage')
                bot.send_message(message.from_user.id, task)
            job = sched.add_job(my_job, 'cron', day=int(times[0]), hour=7, minute=0, replace_existing=True)
            sched.start()  # в 9 часов утра (+2 часа) из-за сервера
            while a[-1] in for_reminder[message.from_user.id]:
                continue
            else:
                job.remove()
                return


try:
    bot.polling(none_stop=True, interval=0)
except Exception as e:
    print(e)
