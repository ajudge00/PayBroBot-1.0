import os
import re
import bcrypt

from models.user import User
from utils.dao import Dao
from utils import globals


def is_valid_password(password):
    pattern = r'^(?=.*[0-9].*[0-9])(?=.*[!@#$%^&*]).{8,}$'
    return bool(re.match(pattern, password))


def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password, hashed_password)


state = ""


class UserOps:
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
            if Dao.get_user_by(username=username) is not None:
                globals.BOT.reply_to(message, "Ilyen felhasználónév már létezik!")
                return

            user = User(-1, username, first_name, last_name, password, acc_number)
            Dao.insert_user(user)
        else:
            globals.BOT.reply_to(message, "Nem adtál meg minden adatot!")

    @staticmethod
    def login_username(message):
        username = message.text.strip()

        if Dao.get_user_by(username=username) is None:
            globals.BOT.reply_to(message, "Ilyen felhasználó nem létezik!")
            return

        user_in_db = Dao.get_user_by(username=username)
        sent_msg = globals.BOT.send_message(message.chat.id, "Mi a jelszavad?")
        globals.BOT.register_next_step_handler(sent_msg, UserOps.login_password, user_in_db)

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
            globals.BOT.register_next_step_handler(sent_msg, UserOps.login_password, user_in_db)

    @staticmethod
    def logout_user(message):
        globals.LOGGED_IN = False
        globals.CURRENT_USER = None
        os.remove("session_dump.json")
        globals.BOT.send_message(message.chat.id, "Kijelentkeztél.")


class AccountOps:

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

            globals.BOT.register_next_step_handler(sent_msg, AccountOps.new_transfer)
        elif state == "user_provided" or state == "account_provided":
            user_to_transfer_to = message.text.strip()

            if state == "user_provided":
                beneficiary = Dao.get_user_by(username=user_to_transfer_to)
            else:
                beneficiary = Dao.get_user_by(account_num=user_to_transfer_to)

            if beneficiary is not None:
                if beneficiary.user_id == globals.CURRENT_USER.user_id:
                    globals.BOT.send_message(message.chat.id, "Nem utalhatsz magadnak pénzt!")
                else:
                    balance = Dao.get_balance_by_user_id(globals.CURRENT_USER.user_id)

                    sent_msg = globals.BOT.send_message(message.chat.id,
                                                        globals.LONG_TEXTS['transfer_pocket_amount'] + str(balance))
                    state = "pocket_amount_provided"
                    globals.BOT.register_next_step_handler(sent_msg, AccountOps.new_transfer, beneficiary)
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
                Dao.change_balance_by_user(beneficiary.user_id, amount=amount)
                Dao.change_balance_by_user(globals.CURRENT_USER.user_id, pocket_name=pocket, amount=-amount)

                balance = Dao.get_balance_by_user_id(globals.CURRENT_USER.user_id)
                globals.BOT.send_message(message.chat.id, "Sikeres átutalás!\n\nÚj egyenleged: \n" + str(balance))
