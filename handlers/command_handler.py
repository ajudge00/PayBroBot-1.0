from utils import globals
from telebot import types
from handlers.controller import UserOps, AccountOps


def set_chat_id(chat_id: int):
    if globals.CHAT_ID == -1:
        globals.CHAT_ID = chat_id


@globals.BOT.message_handler(commands=['status'])
def status(message):
    globals.BOT.send_message(message.chat.id, f"CHAT_ID: {globals.CHAT_ID}\nLOGGED_IN: {globals.LOGGED_IN}\n" +
                             "CURRENT_USER: {globals.CURRENT_USER.username}")


@globals.BOT.message_handler(commands=['start', 'help', 'cancel'])
def start_help(message):
    set_chat_id(message.chat.id)
    text = "Üdvözöl a Fizess, Tesó!\n\n"
    if globals.LOGGED_IN:
        globals.BOT.send_message(message.chat.id, text + globals.LONG_TEXTS['help_text_logged_in'])
    else:
        globals.BOT.send_message(message.chat.id, text + globals.LONG_TEXTS['help_text_not_logged_in'])


@globals.BOT.message_handler(commands=['login'])
def login(message):
    set_chat_id(message.chat.id)
    if globals.LOGGED_IN:
        pass
    else:
        sent_msg = globals.BOT.send_message(message.chat.id, "Mi a felhasználóneved?")
        globals.BOT.register_next_step_handler(sent_msg, UserOps.login_username)


@globals.BOT.message_handler(commands=['logout'])
def logout(message):
    set_chat_id(message.chat.id)
    if globals.LOGGED_IN:
        UserOps.logout_user(message)
    else:
        globals.BOT.send_message(message.chat.id, "Nem vagy bejelentkezve. /login")


@globals.BOT.message_handler(commands=['new_user'])
def new_user(message):
    set_chat_id(message.chat.id)
    sent_msg = globals.BOT.send_message(message.chat.id, globals.LONG_TEXTS['new_user_text'], parse_mode='HTML')
    globals.BOT.register_next_step_handler(sent_msg, UserOps.create_user)


@globals.BOT.message_handler(commands=['new_transfer'])
def new_transfer(message):
    set_chat_id(message.chat.id)
    if globals.LOGGED_IN:

        button_choice_user = types.KeyboardButton('Felhasználónév alapján')
        button_choice_acc = types.KeyboardButton('Számlaszám alapján')

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard.add(button_choice_user)
        keyboard.add(button_choice_acc)

        sent_msg = globals.BOT.send_message(message.chat.id, text="Felhasználónév vagy számlaszám alapján szeretnél "
                                                                  "utalni?", reply_markup=keyboard)
        globals.BOT.register_next_step_handler(sent_msg, AccountOps.new_transfer)
    else:
        globals.BOT.send_message(message.chat.id, globals.LONG_TEXTS['login_warning'])


@globals.BOT.message_handler(commands=['list_transfers'])
def list_transfers(message):
    set_chat_id(message.chat.id)
    pass


@globals.BOT.message_handler(commands=['manage_pockets'])
def manage_pockets(message):
    set_chat_id(message.chat.id)
    pass


@globals.BOT.message_handler(commands=['see_dough'])
def see_dough(message):
    set_chat_id(message.chat.id)
    pass


@globals.BOT.message_handler(commands=['get_notifications'])
def get_notifications(message):
    set_chat_id(message.chat.id)
    pass


@globals.BOT.message_handler(commands=['get_stats'])
def get_stats(message):
    set_chat_id(message.chat.id)
    pass
