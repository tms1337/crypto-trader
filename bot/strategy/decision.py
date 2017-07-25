import logging
from enum import Enum, unique

from bot.util.logging import LoggableMixin


@unique
class OfferType(Enum):
    BUY = 1
    SELL = 2


class Decision(LoggableMixin):
    base_currency = None
    quote_currency = None
    transaction_type = None
    volume = None
    price = None
    exchange = None
    decider = None

    def __init__(self):
        LoggableMixin.__init__(self, Decision)

    def is_valid(self):
        is_invalid = self.base_currency is None or \
                     self.quote_currency is None or \
                     self.transaction_type is None or \
                     self.volume is None or \
                     self.exchange is None or \
                     self.decider is None

        return not is_invalid

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


class ExecutedDecision:
    exchange = None
    id = None
