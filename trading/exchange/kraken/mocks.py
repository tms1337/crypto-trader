from .base import KrakenProvider
from ..base import CurrencyMixin, TradeProvider

from .stats import KrakenStatsProvider


class PrivateKrakenProviderMock(KrakenProvider):
    def __init__(self, base_currency, quote_currency):
        super(PrivateKrakenProviderMock, self).__init__(base_currency, quote_currency)


class TradeProviderMock(PrivateKrakenProviderMock,
                        CurrencyMixin,
                        TradeProvider):
    def __init__(self,
                 base_currency,
                 quote_currency,
                 initial_balance=100,
                 verbose=0):

        PrivateKrakenProviderMock.__init__(self, base_currency, quote_currency)
        CurrencyMixin.__init__(self, base_currency, quote_currency)

        self.verbose = verbose

        self.balance = {self.base_currency: initial_balance,
                        self.quote_currency: initial_balance}

        self.stats = KrakenStatsProvider(base_currency=self.base_currency,
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

    def _create_market_buy_offer(self, volume):
        last_closing_price = self.stats.last_close()

        self.balance[self.base_currency] += volume
        self.balance[self.quote_currency] -= volume * last_closing_price

    def _create_market_sell_offer(self, volume):
        last_closing_price = self.stats.last_close()

        self.balance[self.base_currency] -= volume
        self.balance[self.quote_currency] += volume * last_closing_price
