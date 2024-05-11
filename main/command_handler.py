from utils import globals
from main.convo_handler import UserHandler, AccountHandler, TransferHandler


def set_chat_id(chat_id):
    if globals.CHAT_ID == -1:
        globals.CHAT_ID = chat_id
        print("chat_id set")


@globals.BOT.message_handler(commands=['status'])
def status(message):
    globals.BOT.send_message(
        message.chat.id,
        f"CHAT_ID: {globals.CHAT_ID}\n"
        f"LOGGED_IN: {globals.LOGGED_IN}\n" +
        f"CURRENT_USER: {globals.CURRENT_USER.username if globals.LOGGED_IN else 'None'}")


@globals.BOT.message_handler(commands=['start', 'help', 'cancel'])
def start_help(message):
    set_chat_id(message.chat.id)
    text = "Üdvözöl a Fizess, Tesó!\n\n"
    if globals.LOGGED_IN:
        globals.BOT.send_message(message.chat.id, text + globals.LONG_TEXTS['help_text_logged_in'])
    else:
        globals.BOT.send_message(message.chat.id,
                                 text + globals.LONG_TEXTS['help_text_not_logged_in'])


@globals.BOT.message_handler(commands=['login'])
def login(message):
    set_chat_id(message.chat.id)
    if globals.LOGGED_IN:
        globals.BOT.send_message(message.chat.id, "Már be vagy jelentkezve. Kijelentkezés: /logout")
    else:
        sent_msg = globals.BOT.send_message(
            message.chat.id,
            "Kérlek írd be a felhasználóneved és a jelszavad, <b>vesszővel elválasztva</b>!\n"
            "Pl. user_ursula123, jelszo192168",
            parse_mode="HTML")
        globals.BOT.register_next_step_handler(sent_msg, UserHandler.login)


@globals.BOT.message_handler(commands=['logout'])
def logout(message):
    set_chat_id(message.chat.id)
    if globals.LOGGED_IN:
        UserHandler.logout_user(message)
    else:
        globals.BOT.send_message(message.chat.id, "Nem vagy bejelentkezve. /login")


@globals.BOT.message_handler(commands=['new_user'])
def new_user(message):
    set_chat_id(message.chat.id)
    sent_msg = globals.BOT.send_message(message.chat.id,
                                        globals.LONG_TEXTS['new_user_text'], parse_mode='HTML')
    globals.BOT.register_next_step_handler(sent_msg, UserHandler.create_user)


@globals.BOT.message_handler(commands=['new_transfer'])
def new_transfer(message):
    set_chat_id(message.chat.id)
    if globals.LOGGED_IN:
        if message.text == '/new_transfer':
            keyboard = globals.keyboard_maker([
                globals.ButtonTexts.TRANSFER_BY_USER,
                globals.ButtonTexts.TRANSFER_BY_ACCOUNT_NUM
            ])
            sent_msg = globals.BOT.send_message(
                message.chat.id,
                text="Felhasználónév vagy számlaszám alapján szeretnél utalni?",
                reply_markup=keyboard)
            globals.BOT.register_next_step_handler(sent_msg, TransferHandler.new_transfer)
    else:
        globals.BOT.send_message(message.chat.id, globals.LONG_TEXTS['login_warning'])


@globals.BOT.message_handler(commands=['list_transfers'])
def list_transfers(message):
    set_chat_id(message.chat.id)
    if globals.LOGGED_IN:
        TransferHandler.list_transfers(message)
    else:
        globals.BOT.send_message(message.chat.id, "Nem vagy bejelentkezve. /login")


@globals.BOT.message_handler(commands=['manage_pockets'])
def manage_pockets(message):
    set_chat_id(message.chat.id)
    if globals.LOGGED_IN:
        AccountHandler.manage_pockets(message)
    else:
        globals.BOT.send_message(message.chat.id, "Nem vagy bejelentkezve. /login")


@globals.BOT.message_handler(commands=['see_dough'])
def see_dough(message):
    set_chat_id(message.chat.id)
    globals.BOT.send_message(
        message.chat.id,
        "Egyenleged:\n--------------------\n" +
        str(globals.CURRENT_USER.balance)
    )


@globals.BOT.message_handler(commands=['get_stats'])
def get_stats(message):
    set_chat_id(message.chat.id)
