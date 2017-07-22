from trading.exchange.kraken.trade import KrakenTradeProvider
from trading.exchange.kraken.base import KrakenProvider
from trading.exchange.base import CurrencyMixin, TradeProvider, StatsProvider

from trading.exchange.kraken.stats import KrakenStatsProvider


class StatsProviderMock(StatsProvider):
    def __init__(self,
                 high_array,
                 low_array,
                 last_array):
        self.low_array = low_array
        self.high_array = high_array
        self.last_array = last_array

        self.i = 0

        StatsProvider.__init__(self)

    def ticker_high(self):
        result = self.high_array[self.i]

        return result

    def ticker_low(self):
        result = self.low_array[self.i]

        return result

    def ticker_last(self):
        result = self.last_array[self.i]
        self.i += 1

        return result


class TradeProviderMock(TradeProvider):
    def __init__(self):
        TradeProvider.__init__(self)

    def total_balance(self, currency=None):
        return 100.0

    def create_buy_offer(self, volume, price=None):
        pass

    def create_sell_offer(self, volume, price=None):
        pass
