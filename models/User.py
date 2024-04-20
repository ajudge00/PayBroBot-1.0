from models.Balance import Balance


class User:
    def __init__(self, username: str, acc_number: str, password: str, firstname: str, lastname: str):
        self.username = username
        self.acc_number = acc_number
        self.password = password
        self.firstname = firstname
        self.lastname = lastname
        self.balance = Balance({'noname': 10000})

    def __str__(self):
        return f'{self.username} {self.acc_number} {self.password} {self.firstname} {self.lastname} {self.balance}'
