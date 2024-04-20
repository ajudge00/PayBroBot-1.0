import os
import sqlite3
from typing import Final
import telebot
import json

TOKEN: Final = open("token.txt", 'r').read()

BOT: Final = telebot.TeleBot(TOKEN)

long_texts_path = os.path.join(os.path.dirname(__file__), 'long_texts.json')
LONG_TEXTS: Final = json.load(open(long_texts_path, "r", encoding="utf-8"))

DB_CONN: Final = sqlite3.connect("database.db", check_same_thread=False)
DB_CURSOR: Final = DB_CONN.cursor()