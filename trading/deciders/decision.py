from enum import Enum, unique


@unique
class TransactionType(Enum):
    BUY = 1
    SELL = 2


class Decision:
    currency_pair = None
    transaction_type = None
    volume = None
    price = None

    def is_valid(self):
        is_invalid = self.currency_pair is None or \
                     self.transaction_type is None \
                     or self.volume is None

        return not is_invalid

    def check_validity(self):
        if not self.is_valid():
            raise AssertionError("All fileds must be set")

    def __str__(self):
        string_representations = "currency: %s, type: %s, volume: %s" % (self.currency_pair,
                                                                         self.transaction_type,
                                                                         self.volume)

        if self.price is not None:
            string_representations += ", price: %s" % self.price

        return string_representations

    def __repr__(self):
        return self.__str__()
