from utils.globals import BOT
from utils.globals import LONG_TEXTS
from handlers.user_handlers import UserHandlers


class CommandHandlers:
    @staticmethod
    @BOT.message_handler(commands=['start', 'hello'])
    def send_welcome(message):
        text = "Üdvözöl a Fizess, Tesó!\nA kommandokhoz... /help"
        BOT.send_message(message.chat.id, text, parse_mode="Markdown")

    @staticmethod
    @BOT.message_handler(commands=['help'])
    def send_help(message):
        BOT.send_message(message.chat.id, LONG_TEXTS['help_text'])

    @staticmethod
    @BOT.message_handler(commands=['new_account'])
    def create_new_account(message):
        sent_msg = BOT.send_message(message.chat.id, LONG_TEXTS['new_account_text'])
        BOT.register_next_step_handler(sent_msg, UserHandlers.create_account)