"""
    A felhasználót reprezentáló osztály.
"""

from paybrobot.models.balance import Balance


class User:
    def __init__(self, user_id: int, username: str, first_name: str, last_name: str,
                 password: str, account_num: str, balance: Balance = Balance({'default': 10000})):
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.password = password
        self.account_num = account_num
        self.balance = balance

    def __str__(self):
        return (f'{self.user_id} {self.username} {self.account_num} '
                f'{self.password} {self.first_name} {self.last_name} {self.balance}')
