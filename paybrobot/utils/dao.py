import sqlite3
from datetime import datetime
from paybrobot.models.balance import Balance

import bcrypt

from paybrobot.models.user import User


def get_hashed_password(plain_text_password):
    bytes = plain_text_password.encode('utf-8')
    return bcrypt.hashpw(bytes, bcrypt.gensalt())


class UserDao:
    _instance = None

    def __new__(cls, conn, cursor):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.conn = conn
            cls._instance.cursor = cursor
        return cls._instance

    def create_user(self, user: User):
        # user létrehozása a db-ben
        stmt = "INSERT INTO users(username, first_name, last_name, password, account_num) VALUES(?, ?, ?, ?, ?)"

        self.cursor.execute(stmt, (
            user.username,
            user.first_name,
            user.last_name,
            get_hashed_password(user.password),
            user.account_num
        ))

        self.conn.commit()

        # balance létrehozása default zsebbel
        stmt = "SELECT user_id from users where username = ?"
        user_id_in_db = self.cursor.execute(stmt, (user.username,)).fetchone()[0]

        stmt = "INSERT INTO balances(user_id, pocket_name, balance) VALUES(?, 'default', 10000)"
        self.cursor.execute(stmt, (user_id_in_db,))
        self.conn.commit()

    def get_user_by(self, user_id: int = None, username: str = None, account_num: str = None):
        param_cnt = sum(1 for param in (user_id, username, account_num) if param is not None)

        if param_cnt != 1:
            raise ValueError("Egyszerre csak pontosan egy paraméter használható.")

        stmt = "SELECT * FROM users WHERE "
        res = None

        if user_id is not None:
            stmt += "user_id = ?"
            res = self.cursor.execute(stmt, (user_id,))
        elif username is not None:
            stmt += "username = ?"
            res = self.cursor.execute(stmt, (username,))
        elif account_num is not None:
            stmt += "account_num = ?"
            res = self.cursor.execute(stmt, (account_num,))

        result = res.fetchone()
        if result is not None:
            from paybrobot.utils import globals
            user_id_in_db, username_in_db, first_name, last_name, password, account_num_in_db, twofa = result
            balance = globals.accountdao_inst.get_balance_by_user_id(user_id_in_db)
            user = User(user_id_in_db, username_in_db, first_name, last_name, password, account_num_in_db, balance)
        else:
            return None

        return user


class AccountDao:
    _instance = None

    def __new__(cls, conn, cursor):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.conn = conn
            cls._instance.cursor = cursor
        return cls._instance

    def get_balance_by_user_id(self, user_id):
        stmt = "SELECT * FROM balances WHERE user_id = ?"

        res = self.cursor.execute(stmt, (user_id,))
        result = res.fetchall()

        if len(result) != 0:
            pockets = {}
            for row in result:
                pocket_id, user_id_in_db, pocket_name, balance_in_db = row
                pockets[pocket_name] = balance_in_db

            balance = Balance(pockets)
            return balance

        return None

    def insert_pocket(self, user: User, pocket_name: str) -> bool:
        # helyi
        pockets = user.balance.pockets
        if len(pockets.keys()) == 4:
            raise IOError('Felhasználónként csak 4 zseb lehet.')
        elif pocket_name in pockets.keys():
            raise ValueError('Van már ilyen nevű zseb.')
        else:
            # helyi
            pockets[pocket_name] = 0

        try:
            # db
            sql = "INSERT INTO balances(user_id, pocket_name) VALUES(?,?)"
            self.cursor.execute(sql, (user.user_id, pocket_name))

            self.conn.commit()
            return True
        except (IOError, ValueError, sqlite3.Error) as e:
            print("Error:", e)
            self.conn.rollback()
            return False

    def rename_pocket(self, user: User, old_pocket_name, new_pocket_name) -> bool:
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
        try:
            sql = 'UPDATE balances SET pocket_name = ? WHERE pocket_name = ? AND user_id = ?'
            self.cursor.execute(sql, (new_pocket_name, old_pocket_name, user.user_id))

            self.conn.commit()
            return True
        except (IOError, ValueError, sqlite3.Error) as e:
            print("Error:", e)
            self.conn.rollback()
            return False

    def change_balance(self, user: User, pocket_name: str = None, amount: int = 0, nullify: bool = False) -> bool:
        pockets = user.balance.pockets

        # ha nincs megadva a zseb neve, akkor kiválasztjuk az elsőt, és azt módosítjuk
        if pocket_name is None:
            pocket_name = list(pockets.keys())[0]
        elif pocket_name not in pockets.keys():
            raise IOError('Nincs ilyen nevű zseb.')

        # helyi
        multiplier = 0 if nullify else 1
        pockets[pocket_name] += amount
        pockets[pocket_name] *= multiplier

        # db
        try:
            stmt = 'UPDATE balances SET balance = (balance + ?) * ? WHERE user_id = ? and pocket_name = ?'
            self.cursor.execute(stmt, (amount, multiplier, user.user_id, pocket_name))

            self.conn.commit()
            print(f"new balance of pocket'{pocket_name}' is {pockets[pocket_name]}")
            return True
        except (IOError, ValueError, sqlite3.Error) as e:
            print("Error:", e)
            self.conn.rollback()
            return False

    def remove_pocket(self, user: User, pocket_name) -> bool:
        pockets = user.balance.pockets
        if pocket_name not in pockets.keys():
            raise IOError('Nincs ilyen nevű zseb.')
        elif pockets[pocket_name] != 0:
            raise Exception('Ez a zseb nem üres.')
        else:
            try:
                # helyi
                del pockets[pocket_name]
                # db
                sql = "DELETE FROM balances WHERE pocket_name = ? and user_id = ?"
                self.cursor.execute(sql, (pocket_name, user.user_id))

                self.conn.commit()
                return True
            except (IOError, ValueError, sqlite3.Error) as e:
                print("Error:", e)
                self.conn.rollback()
                return False


class TransferDao:
    _instance = None

    def __new__(cls, conn, cursor):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.conn = conn
            cls._instance.cursor = cursor
        return cls._instance

    def log_transfer(self, sender_id, beneficiary, amount) -> bool:
        if sender_id is None or beneficiary is None:
            raise IOError("A küldő vagy fogadó nem lehet null!")

        try:
            stmt = "INSERT INTO transfers(sender_id, receiver_id, amount, timestamp) VALUES(?, ?, ?, ?)"
            self.cursor.execute(stmt, (sender_id, beneficiary, amount, datetime.now()))

            self.conn.commit()
            return True
        except (IOError, ValueError, sqlite3.Error) as e:
            print("Error:", e)
            self.conn.rollback()
            return False

    def list_transfers(self, user: User, date_filter=None):
        user_id = user.user_id

        stmt = """
                SELECT
                    strftime('%Y-%m-%d %H:%M:%S', t.timestamp) as timestamp,
                    s.user_id, s.username, s.first_name, s.last_name,
                    r.user_id, r.username, r.first_name, r.last_name,
                    t.amount
                FROM transfers t
                LEFT JOIN users s ON t.sender_id = s.user_id
                LEFT JOIN users r ON t.receiver_id = r.user_id
                WHERE (t.sender_id = ? or t.receiver_id = ?)
                """

        if date_filter is None:
            stmt += " ORDER BY t.timestamp DESC"
            self.cursor.execute(stmt, (user_id, user_id))
        else:
            stmt += " and date(t.timestamp) >= ? ORDER BY t.timestamp DESC"
            self.cursor.execute(stmt, (user_id, user_id, date_filter))

        result = self.cursor.fetchall()

        from paybrobot.utils.globals import number_formatter
        transfers = []

        for row in result:
            (timestamp, s_user_id, sender_username, sender_first_name, sender_last_name,
             r_user_id, rec_username, rec_first_name, rec_last_name, amount) = row
            emoji = '↗' if s_user_id != user_id else '↘'
            tipus = "Bejövő" if s_user_id != user_id else "Kimenő"

            transaction = {
                "Típus": f"{tipus}{emoji}",
                "Időpont": timestamp,
                "Küldő": "Te" if s_user_id == user_id else sender_username,
                "Fogadó": "Te" if r_user_id == user_id else rec_username,
                "Összeg": f"{number_formatter(amount)} HUF"
            }

            transfers.append(transaction)

        return transfers
