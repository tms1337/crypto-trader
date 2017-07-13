from trading.exchange.base import CurrencyMixin, StatsProvider
from poloniex import Poloniex
from .base import PoloniexProvider


class PoloniexStatsProvider(CurrencyMixin,
                            StatsProvider,
                            PoloniexProvider):

    def __init__(self, base_currency, quote_currency, api=Poloniex()):
        CurrencyMixin.__init__(base_currency, quote_currency)
        PoloniexProvider.__init__(base_currency, quote_currency, api)

    def ohlc_history(self, interval=1, since=None):
        super().ohlc_history(interval, since)





