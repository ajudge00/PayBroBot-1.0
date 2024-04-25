from models.balance import Balance
from models.user import User
import bcrypt

from utils.globals import DB_CURSOR, DB_CONN


def get_hashed_password(plain_text_password):
    bytes = plain_text_password.encode('utf-8')
    return bcrypt.hashpw(bytes, bcrypt.gensalt())


class Dao:
    @staticmethod
    def insert_user(user: User):
        stmt = "INSERT INTO users(username, first_name, last_name, password, account_num) VALUES(?, ?, ?, ?, ?)"

        DB_CURSOR.execute(stmt, (
            user.username,
            user.first_name,
            user.last_name,
            get_hashed_password(user.password),
            user.account_num
        ))

        DB_CONN.commit()

    @staticmethod
    def get_user_by(user_id: int = None, username: str = None, account_num: str = None) -> User:
        if sum(1 for param in (user_id, username, account_num) if param is not None) > 1:
            raise ValueError("Egyszerre csak pontosan egy paraméter használható.")

        stmt = "SELECT * FROM users WHERE "
        res = None

        if user_id is not None:
            stmt += "user_id = ?"
            res = DB_CURSOR.execute(stmt, (user_id,))
        elif username is not None:
            stmt += "username = ?"
            res = DB_CURSOR.execute(stmt, (username,))
        elif account_num is not None:
            stmt += "account_num = ?"
            res = DB_CURSOR.execute(stmt, (account_num,))

        result = res.fetchone()
        user_id_in_db, username_in_db, first_name, last_name, password, account_num_in_db, twofa = result
        balance = Dao.get_balance_by_user_id(user_id_in_db)
        user = User(user_id_in_db, username_in_db, first_name, last_name, password, account_num_in_db, balance)

        return user

    @staticmethod
    def get_balance_by_user_id(user_id):
        stmt = "SELECT * FROM balances WHERE user_id = ?"

        res = DB_CURSOR.execute(stmt, (user_id,))
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
            res = DB_CURSOR.execute(stmt, (user_id,))
            pocket_name = res.fetchone()[0]

        stmt = 'SELECT balance from balances WHERE user_id = ? AND pocket_name = ?'
        DB_CURSOR.execute(stmt, (user_id, pocket_name))
        balance = DB_CURSOR.fetchone()[0]

        stmt = 'UPDATE balances SET balance = ? WHERE user_id = ? and pocket_name = ?'
        DB_CURSOR.execute(stmt, ((balance + amount), user_id, pocket_name))

        DB_CONN.commit()

    # @staticmethod
    # def get_user_by_account_number(account_num: str):
    #     stmt = "SELECT * FROM users WHERE account_num = ?"
    #
    #     res = DB_CURSOR.execute(stmt, (account_num,))
    #     result = res.fetchall()
    #
    #     user_id_in_db, username, first_name, last_name, password, account_num, twofa = result[0]
    #     balance = Dao.get_balance_by_user_id(user_id_in_db)
    #     user = User(user_id_in_db, username, first_name, last_name, password, account_num, balance)
    #
    #     return user

    # @staticmethod
    # def get_user_by_id(user_id):
    #     stmt = "SELECT * FROM users WHERE user_id = ?"
    #
    #     res = DB_CURSOR.execute(stmt, (user_id,))
    #     result = res.fetchall()
    #
    #     user_id_in_db, username, first_name, last_name, password, account_num, twofa = result[0]
    #     balance = Dao.get_balance_by_user_id(user_id)
    #     user = User(user_id_in_db, username, first_name, last_name, password, account_num, balance)
    #
    #     return user

    # @staticmethod
    # def get_user_by_username(username) -> list[User]:
    #     stmt = "SELECT * FROM users WHERE username = ?"
    #
    #     res = DB_CURSOR.execute(stmt, (username,))
    #     resultset = res.fetchall()
    #
    #     users = []
    #     for row in resultset:
    #         user_id, username, first_name, last_name, password, account_num, twofa = row
    #         balance = Dao.get_balance_by_user_id(user_id)
    #         user = User(user_id, username, first_name, last_name,
    #                     password, account_num, balance if balance != {} else None)
    #         users.append(user)
    #
    #     return users
