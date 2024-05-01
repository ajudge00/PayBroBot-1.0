import os
import sqlite3
from typing import Final
import telebot
import json
from telebot import types



TOKEN: Final = open("token.txt", 'r').read()

BOT: Final = telebot.TeleBot(TOKEN)

long_texts_path = os.path.join(os.path.dirname(__file__), 'long_texts.json')
LONG_TEXTS: Final = json.load(open(long_texts_path, "r", encoding="utf-8"))

DB_CONN: Final = sqlite3.connect("database.db", check_same_thread=False)
DB_CURSOR: Final = DB_CONN.cursor()


# SESSION
LOGGED_IN = False
CURRENT_USER = None
CHAT_ID = -1

try:
    from utils import dao
    session_dump = json.load(open("session_dump.json", "r", encoding="utf-8"))

    user = dao.UserDao.get_user_by(user_id=session_dump['user_id'])

    LOGGED_IN = True
    CURRENT_USER = user
    CHAT_ID = session_dump['chat_id']

    print(f"CHAT_ID: {CHAT_ID}\nLOGGED_IN: {LOGGED_IN}\nCURRENT_USER: {CURRENT_USER.user_id} {CURRENT_USER.username}")
except FileNotFoundError:
    print("no session, i guess")


def number_formatter(number):
    if isinstance(number, float):
        number = int(round(number, 0))

    return "{:,}".format(number).replace(',', '.')


def keyboard_maker(choices: list) -> types.ReplyKeyboardMarkup:
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)

    for choice in choices:
        button = types.KeyboardButton(choice)
        keyboard.add(button)

    return keyboard

