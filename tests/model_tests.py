import unittest

from paybrobot.models.balance import Balance
from paybrobot.models.user import User


class TestBalance(unittest.TestCase):
    """
        A Balance modellhez tartozó tesztesetek.
        Futtasd a gyökérkönyvtárból: pytest ./tests/model_tests.py
    """

    def test_init(self):
        balance = Balance({'default': 10000})
        self.assertEqual(balance.pockets, {'default': 10000})

    def test_str(self):
        balance = Balance({'default': 10000, 'autóra': 20000})
        expected_str = ("Zseb neve: 'default' --- Összeg: 10.000 HUF\n"
                        "Zseb neve: 'autóra' --- Összeg: 20.000 HUF\n"
                        "--------------------\n"
                        "Teljes egyenleg: 30.000 HUF")
        self.assertEqual(str(balance), expected_str)

    def test_get_all_pockets(self):
        balance = Balance({'default': 10000, 'autóra': 20000})
        self.assertEqual(balance.get_all_pockets(), {'default': 10000, 'autóra': 20000})

    def test_get_full_balance(self):
        balance = Balance({'default': 10000, 'autóra': 20000})
        self.assertEqual(balance.get_full_balance(), 30000)

    def test_get_pocket_balance(self):
        balance = Balance({'default': 10000, 'autóra': 20000})
        self.assertEqual(balance.get_pocket_balance('default'), 10000)
        self.assertEqual(balance.get_pocket_balance('autóra'), 20000)

    def test_get_pocket_balance_hianyzo(self):
        balance = Balance({'default': 10000, 'autóra': 20000})
        with self.assertRaises(IOError):
            balance.get_pocket_balance('befektetés')


class UserTests(unittest.TestCase):
    """
        A User modellhez tartozó tesztesetek.
        Futtasd a gyökérkönyvtárból: pytest ./tests/model_tests.py
    """

    def setUp(self):
        pass

    def test_init(self):
        user = User(1, 'username', 'first', 'last', 'password', 'account_num')
        self.assertEqual(user.user_id, 1)
        self.assertEqual(user.username, 'username')
        self.assertEqual(user.first_name, 'first')
        self.assertEqual(user.last_name, 'last')
        self.assertEqual(user.password, 'password')
        self.assertEqual(user.account_num, 'account_num')
        self.assertEqual(user.balance.pockets, {'default': 10000})

    def test_str(self):
        balance = Balance({'default': 10000})
        user = User(1, 'username', 'first', 'last', 'password', 'account_num', balance)
        expected_str = ("1 username account_num password first last "
                        "Zseb neve: 'default' --- Összeg: 10.000 HUF\n"
                        "--------------------\n"
                        "Teljes egyenleg: 10.000 HUF")

        # print(str(user))
        # print(expected_str)
        self.assertEqual(str(user), expected_str)
