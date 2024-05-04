class Balance:
    def __init__(self, pockets=None):
        if pockets is None:
            pockets = {'noname': 10000}
        self.pockets = pockets

    def __str__(self):
        from utils.globals import number_formatter
        balance_str = ""
        for pocket in self.pockets.keys():
            balance_str += (
                f'Zseb neve: \'{pocket}\' --- '
                f'Összeg: {number_formatter(self.pockets[pocket])} HUF\n'
            )

        balance_str += '--------------------\nTeljes egyenleg: ' + number_formatter(self.get_full_balance()) + ' HUF'
        return balance_str

    def get_all_pockets(self) -> dict:
        return self.pockets

    def get_full_balance(self) -> int:
        balance = 0
        for pocket_name in self.pockets.keys():
            balance += self.pockets[pocket_name]

        return balance

    def get_pocket_balance(self, pocket_name: str) -> int:
        if pocket_name not in self.pockets.keys():
            raise IOError('Nincs ilyen nevű pocket')
        return self.pockets[pocket_name]
