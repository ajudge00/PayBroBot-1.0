from datetime import datetime
from models.balance import Balance

import bcrypt

from utils import globals
from models.user import User


def get_hashed_password(plain_text_password):
    bytes = plain_text_password.encode('utf-8')
    return bcrypt.hashpw(bytes, bcrypt.gensalt())


class UserDao:
    @staticmethod
    def create_user(user: User):
        # user létrehozása a db-ben
        stmt = "INSERT INTO users(username, first_name, last_name, password, account_num) VALUES(?, ?, ?, ?, ?)"

        globals.DB_CURSOR.execute(stmt, (
            user.username,
            user.first_name,
            user.last_name,
            get_hashed_password(user.password),
            user.account_num
        ))

        globals.DB_CONN.commit()

        # balance létrehozása default zsebbel
        stmt = "SELECT user_id from users where username = ?"
        user_id_in_db = globals.DB_CURSOR.execute(stmt, (user.username,)).fetchone()[0]

        stmt = "INSERT INTO balances(user_id, pocket_name, balance) VALUES(?, 'default', 10000)"
        globals.DB_CURSOR.execute(stmt, (user_id_in_db,))
        globals.DB_CONN.commit()

    @staticmethod
    def get_user_by(user_id: int = None, username: str = None, account_num: str = None):
        if sum(1 for param in (user_id, username, account_num) if param is not None) > 1:
            raise ValueError("Egyszerre csak pontosan egy paraméter használható.")

        stmt = "SELECT * FROM users WHERE "
        res = None

        if user_id is not None:
            stmt += "user_id = ?"
            res = globals.DB_CURSOR.execute(stmt, (user_id,))
        elif username is not None:
            stmt += "username = ?"
            res = globals.DB_CURSOR.execute(stmt, (username,))
        elif account_num is not None:
            stmt += "account_num = ?"
            res = globals.DB_CURSOR.execute(stmt, (account_num,))

        result = res.fetchone()
        if result is not None:
            user_id_in_db, username_in_db, first_name, last_name, password, account_num_in_db, twofa = result
            balance = BalanceDao.get_balance_by_user_id(user_id_in_db)
            user = User(user_id_in_db, username_in_db, first_name, last_name, password, account_num_in_db, balance)
        else:
            return None

        return user


class BalanceDao:
    @staticmethod
    def get_balance_by_user_id(user_id):
        stmt = "SELECT * FROM balances WHERE user_id = ?"

        res = globals.DB_CURSOR.execute(stmt, (user_id,))
        result = res.fetchall()

        pockets = {}
        for row in result:
            pocket_id, user_id_in_db, pocket_name, balance_in_db = row
            pockets[pocket_name] = balance_in_db

        if len(pockets.keys()) > 0:
            balance = Balance(pockets)
        else:
            balance = Balance(None)

        return balance


    @staticmethod
    def log_transfer(sender_id, beneficiary, amount):
        stmt = "INSERT INTO transfers(sender_id, receiver_id, amount, timestamp) VALUES(?, ?, ?, ?)"
        globals.DB_CURSOR.execute(stmt, (sender_id, beneficiary, amount, datetime.now()))
        globals.DB_CONN.commit()

    @staticmethod
    def list_transfers(user_id):
        stmt = """
            SELECT
                strftime('%Y-%m-%d %H:%M:%S', t.timestamp) as timestamp,
                s.user_id, s.username, s.first_name, s.last_name,
                r.user_id, r.username, r.first_name, r.last_name,
                t.amount
            FROM transfers t
            LEFT JOIN users s ON t.sender_id = s.user_id
            LEFT JOIN users r ON t.receiver_id = r.user_id
            WHERE t.sender_id = ? or t.receiver_id = ?
            """

        globals.DB_CURSOR.execute(stmt, (user_id, user_id))
        result = globals.DB_CURSOR.fetchall()

        res_str = "Tranzakcióid:\n"

        from utils.globals import number_formatter

        for row in result:
            (timestamp, s_user_id, sender_username, sender_first_name, sender_last_name,
             r_user_id, rec_username, rec_first_name, rec_last_name, amount) = row
            emoji = '↗' if s_user_id != user_id else '↘'
            tipus = "Bejövő" if s_user_id != user_id else "Kimenő"

            res_str += "---------------------\n"
            res_str += f"<b>Típus:</b> {tipus}{emoji}\n"
            res_str += f"<b>Időpont:</b> {timestamp}\n"
            res_str += f"<b>Küldő:</b> {'Te' if s_user_id == user_id else sender_username}\n"
            res_str += f"<b>Küldő:</b> {'Te' if r_user_id == user_id else rec_username}\n"
            res_str += f"<b>Összeg:</b> {number_formatter(amount)} HUF\n"

        return res_str

    @staticmethod
    def insert_pocket(user: User, pocket_name: str):
        # helyi
        pockets = user.balance.pockets
        if len(pockets.keys()) == 4:
            raise IOError('Felhasználónként csak 4 zseb lehet.')
        elif pocket_name in pockets.keys():
            raise ValueError('Van már ilyen nevű zseb.')
        else:
            # helyi
            pockets[pocket_name] = 0

        # db
        sql = "INSERT INTO balances(user_id, pocket_name) VALUES(?,?)"
        globals.DB_CURSOR.execute(sql, (user.user_id, pocket_name))

        globals.DB_CONN.commit()

    @staticmethod
    def rename_pocket(user: User, old_pocket_name, new_pocket_name):
        # helyi
        pockets = user.balance.pockets
        if old_pocket_name not in pockets.keys():
            raise IOError('Nincs ilyen nevű zseb!')
        elif new_pocket_name in pockets.keys():
            raise IOError('Van már ilyen nevű zseb!')
        else:
            amount = pockets[old_pocket_name]
            del pockets[old_pocket_name]
            pockets[new_pocket_name] = amount

        # db
        sql = 'UPDATE balances SET pocket_name = ? WHERE pocket_name = ? AND user_id = ?'

        globals.DB_CURSOR.execute(sql, (new_pocket_name, old_pocket_name, user.user_id))
        globals.DB_CONN.commit()

    @staticmethod
    def change_balance(user: User, pocket_name: str = None, amount: int = 0, nullify: bool = False):
        pockets = user.balance.pockets

        # ha nincs megadva a zseb neve, akkor kiválasztjuk az elsőt, és azt módosítjuk
        if pocket_name is None:
            # helyi -> első zseb neve
            default_pocket = list(pockets.keys())[0]
            pockets[default_pocket] += amount

            # db -> user első rekordjának a zsebének a neve
            stmt = 'SELECT pocket_name FROM balances WHERE user_id = ?'
            res = globals.DB_CURSOR.execute(stmt, (user.user_id,))
            pocket_name = res.fetchone()[0]

        elif pocket_name not in pockets.keys():
            raise IOError('Nincs ilyen nevű zseb.')

        if nullify:
            stmt = 'UPDATE balances SET balance = 0 WHERE user_id = ? and pocket_name = ?'
            globals.DB_CURSOR.execute(stmt, (user.user_id, pocket_name))
        else:
            stmt = 'UPDATE balances SET balance = balance + ? WHERE user_id = ? and pocket_name = ?'
            globals.DB_CURSOR.execute(stmt, (amount, user.user_id, pocket_name))

        globals.DB_CONN.commit()

    @staticmethod
    def remove_pocket(user: User, pocket_name):
        pockets = user.balance.pockets
        if pocket_name not in pockets.keys():
            raise IOError('Nincs ilyen nevű zseb.')
        elif pockets[pocket_name] != 0:
            raise Exception('Ez a zseb nem üres.')
        else:
            # helyi
            print("REMOVE POCKET C      ALLED")
            del pockets[pocket_name]
            # db
            sql = "DELETE FROM balances WHERE pocket_name = ? and user_id = ?"
            globals.DB_CURSOR.execute(sql, (pocket_name, user.user_id))
            globals.DB_CONN.commit()

