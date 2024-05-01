from datetime import datetime

from models.balance import Balance
from models.user import User
import bcrypt

from utils import globals


def get_hashed_password(plain_text_password):
    bytes = plain_text_password.encode('utf-8')
    return bcrypt.hashpw(bytes, bcrypt.gensalt())


class UserDao:
    @staticmethod
    def create_user(user: User):
        # user létrehozása
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
        user_id_in_db = globals.DB_CURSOR.execute("SELECT user_id from users where username = ?",
                                          (user.username,)).fetchone()[0]
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
            balance = AccountDao.get_balance_by_user_id(user_id_in_db)
            user = User(user_id_in_db, username_in_db, first_name, last_name, password, account_num_in_db, balance)
        else:
            return None

        return user


class AccountDao:
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
    def change_balance_by_user(user_id, pocket_name: str = None, amount: int = 0):
        if pocket_name is None:
            # ha nincs megadva a zseb neve, akkor kiválasztjuk az elsőt, és azt módosítjuk
            stmt = 'SELECT pocket_name FROM balances WHERE user_id = ?'
            res = globals.DB_CURSOR.execute(stmt, (user_id,))
            pocket_name = res.fetchone()[0]

        stmt = 'SELECT balance from balances WHERE user_id = ? AND pocket_name = ?'
        globals.DB_CURSOR.execute(stmt, (user_id, pocket_name))
        balance = globals.DB_CURSOR.fetchone()[0]

        stmt = 'UPDATE balances SET balance = ? WHERE user_id = ? and pocket_name = ?'
        globals.DB_CURSOR.execute(stmt, ((balance + amount), user_id, pocket_name))

        globals.DB_CONN.commit()

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
    def insert_pocket(name: str):
        print("insert pocket: ", globals.CURRENT_USER.user_id)
        sql = f"INSERT INTO balances(user_id, pocket_name) VALUES(?,?)"
        globals.DB_CURSOR.execute(sql, (globals.CURRENT_USER.user_id, name))

        globals.DB_CONN.commit()
