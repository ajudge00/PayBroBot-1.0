import re

import bcrypt

from models.User import User
from utils.globals import BOT, DB_CURSOR, DB_CONN


def is_valid_password(password):
    pattern = r'^(?=.*[0-9].*[0-9])(?=.*[!@#$%^&*]).{8,}$'
    return bool(re.match(pattern, password))

def get_hashed_password(plain_text_password):
    bytes = plain_text_password.encode('utf-8')
    return bcrypt.hashpw(bytes, bcrypt.gensalt())


class UserHandlers:
    @staticmethod
    def create_account(message):
        lines = message.text.strip().split('\n')

        username = None
        acc_number = None
        password = None
        firstname = None
        lastname = None

        for line in lines:
            key, value = line.split(' - ')
            key = key.strip().lower()
            value = value.strip()

            if key == 'username':
                if len(value) < 6:
                    BOT.reply_to(message, "Felhasználónév nem elég hosszú :/")
                    return
                username = value
            elif key == 'account_number':
                acc_number = value
            elif key == 'password':
                if not is_valid_password(value):
                    BOT.reply_to(message, "Jelszó nem megfelelő")
                    return
                password = value
            elif key == 'firstname':
                firstname = value
            elif key == 'lastname':
                lastname = value
            else:
                pass

        if username and acc_number and password and firstname and lastname:
            # user = User(username, acc_number, str(get_hashed_password(password)), firstname, lastname)
            DB_CURSOR.execute("INSERT INTO users(username, first_name, last_name, password, account_num)"
                              "VALUES(?, ?, ?, ?, ?)", (username, firstname, lastname, get_hashed_password(password), acc_number))
            DB_CONN.commit()
        else:
            BOT.reply_to(message, "Nem adtál meg minden adatot!")
