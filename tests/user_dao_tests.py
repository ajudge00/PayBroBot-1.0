import os
import sqlite3
import unittest
import bcrypt

from paybrobot.models.user import User
from paybrobot.utils.dao import UserDao


def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password, hashed_password)


class UserDaoTests(unittest.TestCase):
    """
        dao.UserDao tesztesetek.
        Futtasd a gyökérkönyvtárból: pytest ./tests/user_dao_tests.py
        A session_dump.json bekavar, ha létezik, ezért először törlendő.
    """
    def setUp(self):
        file_path = "bot/session_dump.json"

        try:
            os.remove(file_path)
            print("Session dump törölve")
        except Exception as e:
            print(e)

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

            CREATE TABLE balances (
                pocket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                pocket_name TEXT NOT NULL,
                balance REAL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
        """)

        self.conn.commit()

        self.cursor.execute("""
           INSERT INTO users (user_id, username, first_name, last_name, password, account_num)
           VALUES (1, 'teszt_user1', 'Smith', 'Smith', 'password', 111111)
        """)

        self.userdao = UserDao(self.conn, self.cursor)

    def test_create_user(self):
        expected_user = User(2, 'teszt_user2', 'Washington', 'tony', 'password1', '000000')
        self.userdao.create_user(expected_user)

        user_in_db = self.cursor.execute("SELECT * FROM users WHERE user_id = 2").fetchone()

        self.assertEqual(user_in_db[0], expected_user.user_id)
        self.assertEqual(user_in_db[1], expected_user.username)
        self.assertEqual(user_in_db[2], expected_user.first_name)
        self.assertEqual(user_in_db[3], expected_user.last_name)
        self.assertTrue(bcrypt.checkpw(expected_user.password.encode(), user_in_db[4]))
        self.assertEqual(user_in_db[5], expected_user.account_num)

        default_pocket = self.cursor.execute("SELECT * FROM balances WHERE user_id = 2").fetchone()
        self.assertEqual(default_pocket[1], expected_user.user_id)
        self.assertEqual(default_pocket[2], "default")
        self.assertEqual(default_pocket[3], 10000.0)

    def test_get_user_by(self):
        expected_user = User(1, 'teszt_user1', 'Smith', 'Smith', 'password', '111111')

        with self.assertRaises(ValueError):
            self.userdao.get_user_by()

        with self.assertRaises(ValueError):
            self.userdao.get_user_by(user_id=2, username="kiskacsa")

        self.assertEqual(self.userdao.get_user_by(user_id=999), None)
        self.assertEqual(self.userdao.get_user_by(user_id=1).username, expected_user.username)
        self.assertEqual(self.userdao.get_user_by(username="teszt_user1").user_id, expected_user.user_id)
        self.assertEqual(self.userdao.get_user_by(account_num='111111').account_num, expected_user.account_num)
