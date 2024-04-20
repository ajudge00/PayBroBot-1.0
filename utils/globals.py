from typing import Final
import telebot

TOKEN: Final = open('token.txt', 'r').read()
bot: Final = telebot.TeleBot(TOKEN)