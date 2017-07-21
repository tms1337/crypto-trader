from trading.util.logging import LoggableMixin
from .base import BittrexProvider
from ..base import CurrencyMixin, StatsProvider
from .client import bittrex


class BittrexStatsProvider(StatsProvider,
                           BittrexProvider,
                           LoggableMixin):

    def __init__(self,
                 api=bittrex.bittrex(None, None)):

        BittrexProvider.__init__(self, api)
        LoggableMixin.__init__(self, BittrexStatsProvider)

    def ohlc_history(self, interval=1, since=None):
        raise NotImplementedError()

    def ticker_high(self):
        ticker_response = self.api.getticker(market=self.form_pair())
        self._check_response(ticker_response)

        return ticker_response["Ask"]

    def ticker_low(self):
        ticker_response = self.api.getticker(market=self.form_pair())
        self._check_response(ticker_response)

        return ticker_response["Bid"]

    def ticker_last(self):
        ticker_response = self.api.getticker(market=self.form_pair())
        self._check_response(ticker_response)

        return ticker_response["Last"]