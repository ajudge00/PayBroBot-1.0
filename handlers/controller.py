import os
import re
import bcrypt
from telebot import types

from models.user import User
from utils.dao import UserDao, AccountDao
from utils import globals


def is_valid_password(password):
    pattern = r'^(?=.*[0-9].*[0-9])(?=.*[!@#$%^&*]).{8,}$'
    return bool(re.match(pattern, password))


def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password, hashed_password)


state = ""


class UserController:
    @staticmethod
    def create_user(message):
        creds = message.text.split(',')
        creds = [c.strip() for c in creds]

        if len(creds[0]) < 6:
            globals.BOT.reply_to(message, "Felhasználónév nem elég hosszú :/")
            return

        username = creds[0]
        first_name = creds[1]
        last_name = creds[2]
        if not is_valid_password(creds[3]):
            globals.BOT.reply_to(message, "Jelszó nem megfelelő")
            return
        password = creds[3]
        acc_number = creds[4]

        if username and acc_number and password and first_name and last_name:
            if UserDao.get_user_by(username=username) is not None:
                globals.BOT.reply_to(message, "Ilyen felhasználónév már létezik!")
                return

            user = User(-1, username, first_name, last_name, password, acc_number)
            UserDao.create_user(user)
            globals.BOT.send_message(message.chat.id, "Sikeres regisztráció! /login")
        else:
            globals.BOT.reply_to(message, "Nem adtál meg minden adatot!")

    @staticmethod
    def login_username(message):
        username = message.text.strip()

        if UserDao.get_user_by(username=username) is None:
            globals.BOT.reply_to(message, "Ilyen felhasználó nem létezik!")
            return

        user_in_db = UserDao.get_user_by(username=username)
        sent_msg = globals.BOT.send_message(message.chat.id, "Mi a jelszavad?")
        globals.BOT.register_next_step_handler(sent_msg, UserController.login_password, user_in_db)

    @staticmethod
    def login_password(message, user_in_db):
        password = message.text.strip().encode()

        if check_password(password, user_in_db.password):
            globals.LOGGED_IN = True
            globals.CURRENT_USER = user_in_db
            globals.BOT.send_message(message.chat.id, "Sikeres bejelentkezés.")
        else:
            sent_msg = globals.BOT.send_message(message.chat.id, "Helytelen jelszó. Próbáld újra. Vagy /cancel a "
                                                                 "kilépéshez.")
            globals.BOT.register_next_step_handler(sent_msg, UserController.login_password, user_in_db)

    @staticmethod
    def logout_user(message):
        globals.LOGGED_IN = False
        globals.CURRENT_USER = None
        os.remove("session_dump.json")
        globals.BOT.send_message(message.chat.id, "Kijelentkeztél.")


class AccountController:

    @staticmethod
    def new_transfer(message, beneficiary: User = None):
        global state

        if state == "":
            sent_msg = ""
            if message.text == "Felhasználónév alapján":
                sent_msg = globals.BOT.send_message(message.chat.id, "Kérlek add meg a felhasználónevet!")
                state = "user_provided"
            elif message.text == "Számlaszám alapján":
                sent_msg = globals.BOT.send_message(message.chat.id, "Kérlek add meg a számlaszámot!")
                state = "account_provided"

            globals.BOT.register_next_step_handler(sent_msg, AccountController.new_transfer)
        elif state == "user_provided" or state == "account_provided":
            user_to_transfer_to = message.text.strip()

            if state == "user_provided":
                beneficiary = UserDao.get_user_by(username=user_to_transfer_to)
            else:
                beneficiary = UserDao.get_user_by(account_num=user_to_transfer_to)

            if beneficiary is not None:
                if beneficiary.user_id == globals.CURRENT_USER.user_id:
                    globals.BOT.send_message(message.chat.id, "Nem utalhatsz magadnak pénzt!")
                else:
                    balance = AccountDao.get_balance_by_user_id(globals.CURRENT_USER.user_id)

                    sent_msg = globals.BOT.send_message(message.chat.id,
                                                        globals.LONG_TEXTS['transfer_pocket_amount'] + str(balance), parse_mode='HTML')
                    state = "pocket_amount_provided"
                    globals.BOT.register_next_step_handler(sent_msg, AccountController.new_transfer, beneficiary)
            else:
                globals.BOT.send_message(message.chat.id, "Ilyen felhasználó nem létezik. Próbáld újra. /new_transfer")
        elif state == "pocket_amount_provided":
            data = message.text.split(',')
            pocket = data[0].strip()
            amount = int(data[1].strip())

            if pocket not in globals.CURRENT_USER.balance.get_all_pockets().keys():
                globals.BOT.send_message(message.chat.id, "Nincs ilyen nevű zsebed. Próbáld újra. /new_transfer")
            elif amount < 0:
                globals.BOT.send_message(message.chat.id, "Átutalandó összeg nem lehet negatív. /new_transfer")
            elif amount > globals.CURRENT_USER.balance.get_pocket_balance(pocket):
                globals.BOT.send_message(message.chat.id, "Nincs elég fedezet a választott zsebben. /new_transfer")
            else:
                AccountDao.change_balance_by_user(beneficiary.user_id, amount=amount)
                AccountDao.change_balance_by_user(globals.CURRENT_USER.user_id, pocket_name=pocket, amount=-amount)
                AccountDao.log_transfer(sender_id=globals.CURRENT_USER.user_id, beneficiary=beneficiary.user_id, amount=amount)

                balance = AccountDao.get_balance_by_user_id(globals.CURRENT_USER.user_id)
                globals.BOT.send_message(message.chat.id, "Sikeres átutalás!\n\nÚj egyenleged:\n--------------------\n" + str(balance))

        state = ""

    @staticmethod
    def list_transfers(message):
        globals.BOT.send_message(message.chat.id, AccountDao.list_transfers(globals.CURRENT_USER.user_id), parse_mode="HTML")

    @staticmethod
    def manage_pockets(message):
        global state
        pockets = globals.CURRENT_USER.balance.get_all_pockets()

        if state == "":
            choices = []

            # Max. 4 zseb lehet
            if len(pockets.keys()) != 4:
                choices.append('Új zseb létrehozása')

            # Min. 1 zsebnek lennie kell
            if len(pockets.keys()) != 1:
                choices.append('Zseb törlése')

            choices.append('Meglévő zseb módosítása')
            keyboard = globals.keyboard_maker(choices)

            state = "action_provided"
            sent_msg = globals.BOT.send_message(message.chat.id, text="Válassz!", reply_markup=keyboard)
            globals.BOT.register_next_step_handler(sent_msg, AccountController.manage_pockets)

        elif state == "action_provided":
            if message.text == "Új zseb létrehozása":
                sent_msg = globals.BOT.send_message(message.chat.id, "Mi legyen a zseb neve?")
                state = "pocket_name_provided"
                globals.BOT.register_next_step_handler(sent_msg, AccountController.manage_pockets)
            elif message.text == "Zseb törlése":
                pass
            else:
                pass
        elif state == "pocket_name_provided":
            new_pocket_name = message.text.strip()

            if new_pocket_name not in pockets.keys():
                AccountDao.insert_pocket(new_pocket_name)
            else:
                sent_msg = globals.BOT.send_message(message.chat.id, "Ilyen nevű zseb már létezik!")
                state = ""
                globals.BOT.register_next_step_handler(sent_msg, AccountController.manage_pockets)