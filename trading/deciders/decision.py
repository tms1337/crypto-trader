from enum import Enum, unique


@unique
class TransactionType(Enum):
    BUY = 1
    SELL = 2


class Decision:
    base_currency = None
    quote_currency = None
    transaction_type = None
    volume = None
    price = None
    exchange = None

    def is_valid(self):
        is_invalid = self.base_currency is None or \
                     self.quote_currency is None or \
                     self.transaction_type is None or \
                     self.volume is None or \
                     self.exchange is None

        return not is_invalid

    def check_validity(self):
        if not self.is_valid():
            raise AssertionError("All decision fields except price must be set")

    def __str__(self):
        currency_pair = "(%s %s)" % (self.base_currency,
                                     self.quote_currency)
        string_representations = "(currency: %s, type: %s, volume: %s, exchange: %s" % (currency_pair,
                                                                                        self.transaction_type,
                                                                                        self.volume,
                                                                                        self.exchange)

        if self.price is not None:
            string_representations += ", price: %s" % self.price

        string_representations += ")"

        return string_representations

    def __repr__(self):
        return self.__str__()
