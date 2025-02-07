"""
    Globális konstansok, változók, metódusok, enumok
"""

import sqlite3
from enum import Enum
from typing import Final
import telebot
import json
from telebot import types

TOKEN: Final = open("paybrobot/token.txt", 'r').read()
BOT: Final = telebot.TeleBot(TOKEN)
LONG_TEXTS: Final = json.load(open("paybrobot/utils/long_texts.json", "r", encoding="utf-8"))

try:
    DB_CONN: Final = sqlite3.connect("paybrobot/database.db", check_same_thread=False)
    DB_CURSOR: Final = DB_CONN.cursor()

    # DAO INSTANCEK
    from paybrobot.utils import dao
    userdao_inst = dao.UserDao(DB_CONN, DB_CURSOR)
    accountdao_inst = dao.AccountDao(DB_CONN, DB_CURSOR)
    transferdao_inst = dao.TransferDao(DB_CONN, DB_CURSOR)

except sqlite3.Error as e:
    print(e)
    exit(1)

"""
    Session kezelés. Ha van, akkor a session_dump.json-ből
    visszaállításra kerül a nem kijelentkezett session az
    előző futásból.
"""
LOGGED_IN = False
CURRENT_USER = None
CHAT_ID = -1

try:
    session_dump = json.load(open("bot/session_dump.json", "r", encoding="utf-8"))
    user = userdao_inst.get_user_by(user_id=session_dump['user_id'])

    LOGGED_IN = True
    CURRENT_USER = user
    CHAT_ID = session_dump['chat_id']

    print(f"CHAT_ID: {CHAT_ID}\nLOGGED_IN: {LOGGED_IN}\nCURRENT_USER: [{CURRENT_USER.user_id}] {CURRENT_USER.username}")
except FileNotFoundError:
    print("no session, i guess")


"""
    Globális function-ök, classok
"""
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


class ButtonTexts(str, Enum):
    """
        Szövegek a gombokra.
        Így nem string literálokkal kell if-ezni...
    """

    TRANSFER_BY_USER = 'Felhasználónév alapján'
    TRANSFER_BY_ACCOUNT_NUM = 'Számlaszám alapján'

    NEW_POCKET = 'Új zseb létrehozása'
    REMOVE_POCKET = "Zseb törlése"
    MODIFY_POCKET = "Meglévő zseb módosítása"
    RENAME_POCKET = "Zseb átnevezése"
    TRANSFER_BETWEEN_POCKETS = "Egyenletmozgatás zsebek között"

    ONE_YEAR_ONWARDS = "Az utóbbi egy évben"
    THIS_MONTH = "Ebben a hónapban"
    THIS_WEEK = "Ezen a héten"
    ALL_TRANSFERS = "Összes"
