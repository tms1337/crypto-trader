from trading.exchange.kraken.trade import KrakenTradeProvider
from .base import KrakenProvider
from ..base import CurrencyMixin, TradeProvider

from .stats import KrakenStatsProvider


class PrivateKrakenProviderMock(KrakenProvider):
    def __init__(self, base_currency, quote_currency):
        super(PrivateKrakenProviderMock, self).__init__(base_currency, quote_currency)


class StatsProviderMock(KrakenStatsProvider):
    def __init__(self,
                 high_array,
                 low_array,
                 last_array):
        KrakenStatsProvider.__init__(self)

        self.low_array = low_array
        self.high_array = high_array
        self.last_array = last_array

        self.i = 0

    def ticker_high(self):
        result = self.high_array[self.i]

        return result

    def ticker_low(self):
        result = self.low_array[self.i]
        self.i += 1

        return result

    def ticker_last(self):
        result = self.last_array[self.i]
        self.i += 1

        return result


class TradeProviderMock(KrakenTradeProvider):
    def __init__(self, key_uri=None, base_currency=None, quote_currency=None, api=None):
        pass

    def total_balance(self, currency=None):
        return 100.0

    def create_buy_offer(self, volume, price=None):
        pass

    def create_sell_offer(self, volume, price=None):
        pass
