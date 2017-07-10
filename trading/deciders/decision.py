from enum import Enum


class TransactionType(Enum):
    BUY = 1
    SELL = 2


class Decision:
    currency_pair = None
    transaction_type = None
    volume = None

    def is_valid(self):
        is_invalid = self.currency_pair is None or \
                     self.transaction_type is None \
                     or self.volume is None

        return not is_invalid

    def check_validity(self):
        if not self.is_valid():
            raise AssertionError("All fileds must be set")
