import datetime
import os
import re
import bcrypt

from models.user import User
from utils.dao import UserDao, AccountDao, TransferDao
from utils import globals
from utils.globals import ButtonTexts


def is_valid_password(password):
    pattern = r'^(?=.*[0-9].*[0-9])(?=.*[!@#$%^&*]).{8,}$'
    return bool(re.match(pattern, password))


def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password, hashed_password)


STATE = ""


class UserHandler:
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
    def login(message):
        try:
            creds = message.text.split(',')
            provided_username = creds[0].strip()
            provided_password = creds[1].strip().encode()

            user_in_db = UserDao.get_user_by(username=provided_username)

            if user_in_db is None:
                globals.BOT.reply_to(message, "Ilyen felhasználó nem létezik!")
                return

            if check_password(provided_password, user_in_db.password):
                globals.LOGGED_IN = True
                globals.CURRENT_USER = user_in_db
                globals.BOT.send_message(message.chat.id, "Sikeres bejelentkezés.")
            else:
                globals.BOT.send_message(
                    message.chat.id,
                    "Helytelen jelszó. Próbáld újra. Vagy /cancel a kilépéshez.")
        except IndexError:
            globals.BOT.send_message(
                message.chat.id,
                "Az adataid <b>vesszővel elválasztva add meg</b>!", parse_mode="HTML")

    @staticmethod
    def logout_user(message):
        globals.LOGGED_IN = False
        globals.CURRENT_USER = None
        try:
            os.remove("session_dump.json")
        except FileNotFoundError:
            print("User kijelentkeztetve. Még nem jött létre a dump.")
        finally:
            globals.BOT.send_message(message.chat.id, "Kijelentkeztél.")


class AccountHandler:
    @staticmethod
    def manage_pockets(message):
        global STATE
        pockets = globals.CURRENT_USER.balance.get_all_pockets()

        if STATE == "":
            choices = []

            # Max. 4 zseb lehet
            if len(pockets.keys()) != 4:
                choices.append(globals.ButtonTexts.NEW_POCKET)

            # Min. 1 zsebnek lennie kell
            if len(pockets.keys()) != 1:
                choices.append(globals.ButtonTexts.REMOVE_POCKET)

            choices.append(globals.ButtonTexts.MODIFY_POCKET)
            keyboard = globals.keyboard_maker(choices)

            STATE = "action_provided"
            sent_msg = globals.BOT.send_message(message.chat.id, text="Válassz!", reply_markup=keyboard)
            globals.BOT.register_next_step_handler(sent_msg, AccountHandler.manage_pockets)

        elif STATE == "action_provided":
            if message.text == globals.ButtonTexts.NEW_POCKET:
                sent_msg = globals.BOT.send_message(message.chat.id, "Mi legyen az új zseb neve?")
                globals.BOT.register_next_step_handler(sent_msg, AccountHandler.new_pocket)

            elif message.text == globals.ButtonTexts.REMOVE_POCKET:
                choices = []

                for pocket, balance in pockets.items():
                    choices.append(pocket + " - " +
                                   str(globals.number_formatter(balance)) + " HUF")

                keyboard = globals.keyboard_maker(choices)

                sent_msg = globals.BOT.send_message(
                    message.chat.id,
                    "Kérlek válaszd ki a törlendő zsebet!\n",
                    reply_markup=keyboard
                )

                STATE = ""

                globals.BOT.register_next_step_handler(
                    sent_msg,
                    AccountHandler.delete_pocket)

            elif message.text == globals.ButtonTexts.MODIFY_POCKET:
                keyboard = globals.keyboard_maker([
                    globals.ButtonTexts.RENAME_POCKET,
                    globals.ButtonTexts.TRANSFER_BETWEEN_POCKETS
                ])

                sent_msg = globals.BOT.send_message(
                    message.chat.id,
                    "Válassz!",
                    reply_markup=keyboard
                )
                STATE = ""
                globals.BOT.register_next_step_handler(sent_msg, AccountHandler.modify_pocket)
        else:
            print("valami lett a state-tel")

    @staticmethod
    def new_pocket(message):
        global STATE
        pockets = globals.CURRENT_USER.balance.get_all_pockets()
        new_pocket_name = message.text.strip()

        if new_pocket_name not in pockets.keys():
            if AccountDao.insert_pocket(globals.CURRENT_USER, new_pocket_name):
                STATE = ""
                globals.BOT.send_message(message.chat.id, "Zseb létrehozása sikeres! /see_dough")
            else:
                STATE = ""
                globals.BOT.send_message(message.chat.id, "Valami hiba történt.")
        else:
            sent_msg = globals.BOT.send_message(message.chat.id, "Ilyen nevű zseb már létezik!")
            STATE = ""
            AccountHandler.manage_pockets(sent_msg)

    @staticmethod
    def delete_pocket(message, tmp=None):
        global STATE
        pockets = globals.CURRENT_USER.balance.get_all_pockets()
        pocket_to_delete = message.text.split('-')[0].strip()

        if STATE == "":
            if pockets[pocket_to_delete] != 0:
                choices = []

                for pocket, balance in pockets.items():
                    if pocket != pocket_to_delete:
                        choices.append(pocket + " - " +
                                       str(globals.number_formatter(balance)) + " HUF")

                keyboard = globals.keyboard_maker(choices)

                sent_msg = globals.BOT.send_message(
                    message.chat.id,
                    "A törlendő zseb nem üres, így a benne lévő egyenleget "
                    "át kell tenni egy másikba. Melyikbe?",
                    reply_markup=keyboard
                )

                STATE = "to_transfer_to_for_delete_provided"
                globals.BOT.register_next_step_handler(sent_msg, AccountHandler.delete_pocket, tmp=pocket_to_delete)
            else:
                # globals.CURRENT_USER.balance.remove_pocket(pocket_to_delete)
                if AccountDao.remove_pocket(globals.CURRENT_USER, pocket_to_delete):
                    globals.BOT.send_message(
                        message.chat.id,
                        "Zseb törlése sikeres!\n" +
                        globals.CURRENT_USER.balance
                    )
                else:
                    globals.BOT.send_message(
                        message.chat.id,
                        "A zseb törlése nem sikerült..."
                    )
        elif STATE == "to_transfer_to_for_delete_provided":
            pocket_to_delete = tmp
            pocket_to_transfer_to = message.text.split('-')[0].strip()

            if (AccountDao.change_balance(globals.CURRENT_USER, pocket_to_transfer_to, pockets[pocket_to_delete]) and
                    AccountDao.change_balance(globals.CURRENT_USER, pocket_to_delete, nullify=True) and
                    AccountDao.remove_pocket(globals.CURRENT_USER, pocket_to_delete)):
                globals.BOT.send_message(
                    message.chat.id,
                    "Egyenlegmozgatás és a zseb törlése sikeres!\n" +
                    str(globals.CURRENT_USER.balance)
                )
            else:
                globals.BOT.send_message(message.chat.id, "Valami nem jó :/")

            STATE = ""

    @staticmethod
    def modify_pocket(message):
        if message.text == globals.ButtonTexts.RENAME_POCKET:
            sent_msg = globals.BOT.send_message(
                message.chat.id,
                "Kérlek add meg az átnevezendő zseb nevét és az új nevet, <b>vesszővel elválasztva</b>!",
                parse_mode="HTML"
            )
            globals.BOT.register_next_step_handler(sent_msg, AccountHandler.rename_pocket)
        elif message.text == globals.ButtonTexts.TRANSFER_BETWEEN_POCKETS:
            sent_msg = globals.BOT.send_message(
                message.chat.id,
                "Add meg, melyik zsebből, melyikbe, és mennyit szeretnél átmozgatni.\n"
                "Pl. lakás, autó, 100000"
            )
            globals.BOT.register_next_step_handler(sent_msg, AccountHandler.transfer_between_pockets)

    @staticmethod
    def rename_pocket(message):
        global STATE
        pockets = globals.CURRENT_USER.balance.get_all_pockets()

        to_rename = message.text.split(",")[0].strip()
        new_name = message.text.split(",")[1].strip()

        if to_rename not in pockets.keys():
            globals.BOT.send_message(message.chat.id, "Nincs ilyen nevű zsebed!")
        elif new_name in pockets.keys():
            globals.BOT.send_message(message.chat.id, "Van már ilyen nevű zseb!")
        else:
            if AccountDao.rename_pocket(globals.CURRENT_USER, to_rename, new_name):
                globals.BOT.send_message(message.chat.id, "Zseb átnevezése sikeres!")
            else:
                globals.BOT.send_message(message.chat.id, "Valami hiba történt...")

        STATE = ""

    @staticmethod
    def transfer_between_pockets(message):
        pockets = globals.CURRENT_USER.balance.get_all_pockets()

        if len(message.text.split(",")) != 3:
            globals.BOT.send_message(message.chat.id, "Nem jó formátumot használtál!")
        else:
            from_pocket = message.text.split(",")[0].strip()
            to_pocket = message.text.split(",")[1].strip()
            amount = int(message.text.split(",")[2].strip())

            if from_pocket not in pockets.keys():
                globals.BOT.send_message(
                    message.chat.id,
                    "Nincs ilyen zsebed: " + from_pocket
                )
            elif to_pocket not in pockets.keys():
                globals.BOT.send_message(
                    message.chat.id,
                    "Nincs ilyen zsebed: " + to_pocket
                )
            elif pockets[from_pocket] < amount:
                globals.BOT.send_message(
                    message.chat.id,
                    f"Nincs elég fedezet a zsebben: {from_pocket}: {pockets[from_pocket]} HUF"
                )
            else:
                if (AccountDao.change_balance(globals.CURRENT_USER, from_pocket, -1 * amount) and
                        AccountDao.change_balance(globals.CURRENT_USER, to_pocket, amount)):
                    globals.BOT.send_message(message.chat.id, "Egyenlegmozgatás sikeres.")
                else:
                    globals.BOT.send_message(message.chat.id, "Valami bibi van...")


class TransferHandler:
    @staticmethod
    def new_transfer(message, beneficiary: User = None):
        global STATE

        if STATE == "":
            if message.text == globals.ButtonTexts.TRANSFER_BY_USER:
                sent_msg = globals.BOT.send_message(
                    message.chat.id, "Kérlek add meg a felhasználónevet!")
                STATE = "user_provided"
            elif message.text == globals.ButtonTexts.TRANSFER_BY_ACCOUNT_NUM:
                sent_msg = globals.BOT.send_message(
                    message.chat.id, "Kérlek add meg a számlaszámot!")
                STATE = "account_provided"
            else:
                sent_msg = globals.BOT.send_message(message.chat.id, "Ezt nem értettem...")

            globals.BOT.register_next_step_handler(sent_msg, TransferHandler.new_transfer)
        elif STATE == "user_provided" or STATE == "account_provided":
            user_to_transfer_to = message.text.strip()

            if STATE == "user_provided":
                beneficiary = UserDao.get_user_by(username=user_to_transfer_to)
            else:
                beneficiary = UserDao.get_user_by(account_num=user_to_transfer_to)

            if beneficiary is not None:
                if beneficiary.user_id == globals.CURRENT_USER.user_id:
                    STATE = ""
                    globals.BOT.send_message(message.chat.id, "Nem utalhatsz magadnak pénzt!")
                else:
                    balance = AccountDao.get_balance_by_user_id(globals.CURRENT_USER.user_id)

                    sent_msg = globals.BOT.send_message(
                        message.chat.id,
                        globals.LONG_TEXTS['transfer_pocket_amount'] +
                        str(balance),
                        parse_mode='HTML')

                    STATE = "pocket_amount_provided"
                    globals.BOT.register_next_step_handler(sent_msg, TransferHandler.new_transfer, beneficiary)
            else:
                STATE = ""
                globals.BOT.send_message(message.chat.id, "Ilyen felhasználó nem létezik. Próbáld újra. /new_transfer")
        elif STATE == "pocket_amount_provided":
            data = message.text.split(',')
            pocket = data[0].strip()
            amount = int(data[1].strip())

            if pocket not in globals.CURRENT_USER.balance.get_all_pockets().keys():
                globals.BOT.send_message(message.chat.id, "Nincs ilyen nevű zsebed. Próbáld újra. /new_transfer")
            elif amount < 0:
                globals.BOT.send_message(message.chat.id, "Az átutalandó összeg nem lehet negatív. /new_transfer")
            elif amount > globals.CURRENT_USER.balance.get_pocket_balance(pocket):
                globals.BOT.send_message(message.chat.id, "Nincs elég fedezet a választott zsebben. /new_transfer")
            else:
                if (AccountDao.change_balance(beneficiary,
                                              amount=amount) and
                        AccountDao.change_balance(globals.CURRENT_USER,
                                                  pocket_name=pocket,
                                                  amount=-amount) and
                        TransferDao.log_transfer(sender_id=globals.CURRENT_USER.user_id,
                                                 beneficiary=beneficiary.user_id,
                                                 amount=amount)):
                    balance = AccountDao.get_balance_by_user_id(globals.CURRENT_USER.user_id)
                    globals.BOT.send_message(
                        message.chat.id,
                        "Sikeres átutalás!\n\nÚj egyenleged:\n--------------------\n"
                        + str(balance))

            STATE = ""

    @staticmethod
    def list_transfers(message):
        global STATE

        if STATE == "":
            choices = [ButtonTexts.ALL_TRANSFERS,
                       ButtonTexts.ONE_YEAR_ONWARDS,
                       ButtonTexts.THIS_MONTH,
                       ButtonTexts.THIS_WEEK]

            keyboard = globals.keyboard_maker(choices)

            sent_msg = globals.BOT.send_message(message.chat.id, "Válassz kezdődátumot!", reply_markup=keyboard)
            STATE = "filter_provided"
            globals.BOT.register_next_step_handler(sent_msg, TransferHandler.list_transfers)
        elif STATE == "filter_provided":
            date_filter = None
            today = datetime.date.today()

            if message.text == ButtonTexts.ONE_YEAR_ONWARDS:
                date_filter = today - datetime.timedelta(days=365)
            elif message.text == ButtonTexts.THIS_MONTH:
                date_filter = today.replace(day=1)
            elif message.text == ButtonTexts.THIS_WEEK:
                day_nth = today.weekday()
                date_filter = today - datetime.timedelta(days=day_nth)

            transfers = TransferDao.list_transfers(globals.CURRENT_USER, date_filter)

            transfers_str = "Tranzakcióid:\n"
            for transfer in transfers:
                transfers_str += "---------------------\n"
                for key, value in transfer.items():
                    transfers_str += f"<b>{key}:</b> {value}\n"

            globals.BOT.send_message(
                message.chat.id, transfers_str,
                parse_mode="HTML")

            STATE = ""
