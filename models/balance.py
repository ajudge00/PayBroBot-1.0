from utils.globals import CURRENT_USER
from utils.dao import BalanceDao


class Balance:
    def __init__(self, pockets=None):
        if pockets is None:
            pockets = {'noname': 10000}
        self._pockets = pockets

    def __str__(self):
        from utils.globals import number_formatter
        balance_str = ""
        for pocket in self._pockets.keys():
            balance_str += (
                f'Zseb neve: \'{pocket}\' --- '
                f'Összeg: {number_formatter(self._pockets[pocket])} HUF\n'
            )

        balance_str += '--------------------\nTeljes egyenleg: ' + number_formatter(self.get_full_balance()) + ' HUF'
        return balance_str

    def add_pocket(self, pocket_name: str):
        if len(self._pockets.keys()) == 4:
            raise IOError('Felhasználónként csak 4 zseb lehet.')
        elif pocket_name in self._pockets.keys():
            raise ValueError('Van már ilyen nevű zseb.')
        else:
            # helyi
            self._pockets[pocket_name] = 0
            # db
            BalanceDao.insert_pocket(pocket_name)

    def remove_pocket(self, pocket_name: str):
        if pocket_name not in self._pockets.keys():
            raise IOError('Nincs ilyen nevű zseb.')
        else:
            # helyi
            del self._pockets[pocket_name]
            # db
            BalanceDao.remove_pocket(pocket_name)

    def change_balance(self, pocket_name: str = None, amount: int = 0):
        if pocket_name is None:
            # helyi
            default_pocket = list(self._pockets.keys())[0]
            self._pockets[default_pocket] += amount
            # db
            BalanceDao.change_balance_by_user(CURRENT_USER.user_id, default_pocket, amount)
        elif pocket_name not in self._pockets.keys():
            raise IOError('Nincs ilyen nevű zseb.')
        else:
            # helyi
            self._pockets[pocket_name] += amount
            # db
            BalanceDao.change_balance_by_user(CURRENT_USER.user_id, pocket_name, amount)

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

    def rename_pocket(self, old_name: str, new_name: str):
        if old_name not in self._pockets.keys():
            raise IOError('Nincs ilyen nevű zseb!')
        elif new_name in self._pockets.keys():
            raise IOError('Van már ilyen nevű zseb!')
        else:
            amount = self._pockets[old_name]
            del self._pockets[old_name]
            self._pockets[new_name] = amount
            BalanceDao.rename_pocket(CURRENT_USER.user_id, old_name, new_name)
