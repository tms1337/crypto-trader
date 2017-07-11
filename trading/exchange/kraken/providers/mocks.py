from .base import Provider

from trading.deciders.decision import TransactionType
from .stats import StatsProvider


class PrivateProviderMock(Provider):
    def __init__(self, base_currency, quote_currency):
        super(PrivateProviderMock, self).__init__(base_currency, quote_currency)


class TradeProviderMock(PrivateProviderMock):
    def __init__(self,
                 base_currency,
                 quote_currency,
                 initial_balance=100,
                 verbose=0):

        super(TradeProviderMock, self).__init__(base_currency,
                                                quote_currency)

        self.verbose = verbose

        self.balance = {self.base_currency: initial_balance,
                        self.quote_currency: initial_balance}

        self.stats = StatsProvider(base_currency=self.base_currency,
                                   quote_currency=self.quote_currency)

    def total_balance(self):
        return self.balance

    def create_buy_offer(self, volume, price=None):
        if price is None:
            self._create_market_buy_offer(volume)
        else:
            raise NotImplementedError("Mock does not support this "
                                      "operation with price parameter")

    def create_sell_offer(self, volume, price=None):
        if price is None:
            self._create_market_sell_offer(volume)
        else:
            raise NotImplementedError("Mock does not support this "
                                      "operation with price parameter")

    def create_bulk_offers(self, decisions):
        failed_decisions = []

        for decision in decisions:
            if decision.currency_pair == self._form_pair():
                try:
                    if decision.transaction_type == TransactionType.BUY:
                        self.create_buy_offer(volume=decision.volume, price=decision.price)
                    elif decision.transaction_type == TransactionType.SELL:
                        self.create_sell_offer(volume=decision.volume, price=decision.price)
                except Exception as ex:
                    failed_decisions.append(decision)
                    if self.verbose >= 1:
                        print("An error has occured, %s" % str(ex))
            else:
                failed_decisions.append(decision)

        return failed_decisions

    def _create_market_buy_offer(self, volume):
        last_closing_price = self.stats.last_close()

        self.balance[self.base_currency] += volume
        self.balance[self.quote_currency] -= volume * last_closing_price

    def _create_market_sell_offer(self, volume):
        last_closing_price = self.stats.last_close()

        self.balance[self.base_currency] -= volume
        self.balance[self.quote_currency] += volume * last_closing_price
