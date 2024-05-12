import sqlite3
import unittest

from paybrobot.models.balance import Balance
from paybrobot.models.user import User
from paybrobot.utils.dao import AccountDao


class AccountDaoTests(unittest.TestCase):
    """
        dao.AccountDao tesztesetek.
        Futtasd a gyökérkönyvtárból: pytest ./tests/account_dao_tests.py
    """
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.conn.executescript("""
            CREATE TABLE balances (
                pocket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                pocket_name TEXT NOT NULL,
                balance REAL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );
        """)

        self.conn.commit()

        self.conn.executescript("""
            INSERT INTO balances (user_id, pocket_name, balance)
            VALUES (1, 'egy', 100);
            INSERT INTO balances (user_id, pocket_name, balance)
            VALUES (1, 'két', 200);
            INSERT INTO balances (user_id, pocket_name, balance)
            VALUES (1, 'há', 300);
            INSERT INTO balances (user_id, pocket_name, balance)
            VALUES (1, 'négy', 400);
            INSERT INTO balances (user_id, pocket_name, balance)
            VALUES (2, 'eggy', 1000);
            INSERT INTO balances (user_id, pocket_name, balance)
            VALUEs (3, 'test', 10)
        """)

        self.conn.commit()
        self.accountdao = AccountDao(self.conn, self.cursor)

    def test_get_balance_by_user_id(self):
        expected_balance = Balance({
            'egy': 200,
            'két': 200,
            'há': 330,
            'négy': 0
        })

        self.assertIsNone(self.accountdao.get_balance_by_user_id(123))
        self.assertEqual(self.accountdao.get_balance_by_user_id(1).pockets, expected_balance.pockets)

        expected_balance = Balance({'eggy': 1000})
        self.assertEqual(self.accountdao.get_balance_by_user_id(2).pockets, expected_balance.pockets)

    def test_insert_pocket(self):
        test_balance1 = Balance({
            'egy': 100,
            'két': 200,
            'há': 300,
            'négy': 400
        })
        test_user1 = User(1, 'bigbro', 'asd',
                          'asd', 'titok', '213321',
                          test_balance1)

        with self.assertRaises(IOError):
            self.accountdao.insert_pocket(test_user1, 'test')

        test_balance2 = Balance({
            'eggy': 1000
        })
        test_user2 = User(2, 'lilbro', 'asd',
                          'asd', 'valami', '24124',
                          test_balance2)
        with self.assertRaises(ValueError):
            self.accountdao.insert_pocket(test_user2, 'eggy')

        test_balance3 = Balance({
            'testttt': 10
        })
        test_user3 = User(3, 'hey', 'asd',
                          'asd', 'elemer', '553135',
                          test_balance3)

        self.assertTrue(self.accountdao.insert_pocket(test_user3, 'valami'))
        self.assertEqual(test_user3.balance.pockets, {'testttt': 10, 'valami': 0})

        self.accountdao.cursor.execute("SELECT * FROM balances WHERE user_id = 3")
        result = self.accountdao.cursor.fetchall()
        self.assertEqual(len(result), 2)

    def test_rename_pocket(self):
        test_balance1 = Balance({
            'egy': 100,
            'két': 200,
            'há': 300,
            'négy': 400
        })
        test_user1 = User(1, 'valami', 'asd',
                          'asd', 'titok', '213321',
                          test_balance1)

        with self.assertRaises(IOError):
            self.accountdao.rename_pocket(test_user1, 'asdasd', 'kati')

        with self.assertRaises(IOError):
            self.accountdao.rename_pocket(test_user1, 'egy', 'két')

        self.accountdao.rename_pocket(test_user1, 'két', 'kettő')
        self.assertEqual(test_user1.balance.pockets, {'egy': 100, 'kettő': 200, 'há': 300, 'négy': 400})

        self.accountdao.cursor.execute("SELECT * FROM balances WHERE user_id = 1 AND pocket_name = 'kettő'")
        result = self.accountdao.cursor.fetchall()
        self.assertEqual(len(result), 1)

    def test_change_balance(self):
        test_balance1 = Balance({
            'egy': 100,
            'két': 200,
            'há': 300,
            'négy': 400
        })
        test_user1 = User(1, 'valami', 'asd',
                          'asd', 'titok', '213321',
                          test_balance1)

        with self.assertRaises(IOError):
            self.accountdao.change_balance(test_user1, 'xyz')

        self.accountdao.change_balance(test_user1, amount=100)
        self.assertEqual(test_user1.balance.pockets["egy"], 200)

        self.accountdao.change_balance(test_user1, 'há', 30)
        self.assertEqual(test_user1.balance.pockets["há"], 330)

        self.accountdao.change_balance(test_user1, 'négy', nullify=True)
        self.assertEqual(test_user1.balance.pockets["négy"], 0)

    def test_remove_pocket(self):
        test_balance1 = Balance({
            'egy': 100,
            'két': 200,
            'há': 300,
            'négy': 400
        })
        test_user1 = User(1, 'valami', 'asd',
                          'asd', 'titok', '213321',
                          test_balance1)

        with self.assertRaises(IOError):
            self.accountdao.remove_pocket(test_user1, 'xyz')

        with self.assertRaises(Exception):
            self.accountdao.remove_pocket(test_user1, 'egy')

        self.accountdao.change_balance(test_user1, 'négy', nullify=True)
        self.accountdao.remove_pocket(test_user1, 'négy')
        self.assertEqual(len(test_user1.balance.pockets.keys()), 3)
