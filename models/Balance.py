class Balance:
    def __init__(self, pockets: dict):
        self._pockets = pockets

    def __str__(self):
        balance_str = ""
        for pocket in self._pockets.keys():
            balance_str += f'{pocket}: {self._pockets[pocket]}\n'
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

    def change_balance(self, pocket_name: str, amount: int):
        if pocket_name not in self._pockets.keys():
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