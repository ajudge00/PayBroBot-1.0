

class Balance:
    def __init__(self, pockets=None):
        if pockets is None:
            pockets = {'noname': 10000}
        self._pockets = pockets

    def __str__(self):
        from utils.globals import number_formatter
        balance_str = ""
        for pocket in self._pockets.keys():
            balance_str += ((f'Zseb neve: \'{pocket}\' --- ' +
                            f'Összeg: {number_formatter(self._pockets[pocket])} HUF\n'))

        balance_str += '--------------------\nTeljes egyenleg: ' + number_formatter(self.get_full_balance()) + ' HUF'
        return balance_str

    def add_pocket(self, pocket_name: str):
        if len(self._pockets.keys()) == 4:
            raise IOError('Max number of pockets reached')
        elif pocket_name in self._pockets.keys():
            raise ValueError('Pocket with this name already exists')
        else:
            self._pockets[pocket_name] = 0

    def remove_pocket(self, pocket_name: str):
        if pocket_name not in self._pockets.keys():
            raise IOError('Pocket with this name does not exist')
        else:
            del self._pockets[pocket_name]

    def change_balance(self, pocket_name: str = None, amount: int = 0):
        if pocket_name is None:
            default_pocket = list(self._pockets.keys())[0]
            self._pockets[default_pocket] += amount
        elif pocket_name not in self._pockets.keys():
            raise IOError('Pocket with this name does not exist')
        else:
            self._pockets[pocket_name] += amount

    def get_all_pockets(self) -> dict:
        return self._pockets

    def get_full_balance(self) -> int:
        balance = 0
        for pocket_name in self._pockets.keys():
            balance += self._pockets[pocket_name]



        return balance

    def get_pocket_balance(self, pocket_name: str) -> int:
        if pocket_name not in self._pockets.keys():
            raise IOError('Pocket with this name does not exist')
        else:
            return self._pockets[pocket_name]
