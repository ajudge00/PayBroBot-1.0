import sqlite3
import unittest
from datetime import datetime, timedelta

from paybrobot.models.user import User
from paybrobot.utils.dao import TransferDao

# unittest.TestLoader.sortTestMethodsUsing = None


class TransferDaoTests(unittest.TestCase):
    """
        dao.TransferDao tesztesetek.
        Futtasd a gyökérkönyvtárból: pytest ./tests/transfer_dao_tests.py
    """
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.conn.executescript("""
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                password TEXT NOT NULL,
                account_num TEXT NOT NULL,
                twofa_enabled INTEGER DEFAULT 0
            );
            
            CREATE TABLE transfers (
                transfer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_id) REFERENCES users(user_id),
                FOREIGN KEY (receiver_id) REFERENCES users(user_id)
            );
        """)

        self.conn.commit()

        self.conn.executescript("""
            INSERT INTO users (username, first_name, last_name, password, account_num)
            VALUES ("user1", "John", "Doe", "1234", "1234");
            INSERT INTO users (username, first_name, last_name, password, account_num)
            VALUES ("user2", "Jane", "Tho", "121212", "11111") 
        """)

        self.conn.commit()
        self.transferdao = TransferDao(self.conn, self.cursor)

    def test_b_log_transfer(self):
        with self.assertRaises(IOError):
            self.transferdao.log_transfer(1, None, 0)

        self.transferdao.log_transfer(1, 2, 10)

        self.transferdao.cursor.execute("SELECT * FROM transfers WHERE sender_id = 1 AND receiver_id = 2")
        result = self.transferdao.cursor.fetchall()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][3], 100)

    def test_a_list_transfers(self):
        self.transferdao.conn.executescript("""
            INSERT INTO transfers (sender_id, receiver_id, amount)
            VALUES (1, 2, 100)
        """)

        self.transferdao.conn.commit()

        expected_list_dict = [
            {
                "Típus": "Kimenő↘",
                "Küldő": "Te",
                "Fogadó": "user2",
                "Összeg": str(100) + " HUF"
            }
        ]

        user1 = User(1, "user1", "John", "Doe", "1234", "1234")
        res = self.transferdao.list_transfers(user1)

        for transfer in res:
            del transfer["Időpont"]

        self.assertEqual(res, expected_list_dict)
