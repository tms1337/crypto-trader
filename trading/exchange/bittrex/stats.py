from .base import BittrexProvider
from ..base import CurrencyMixin, StatsProvider
from .client import bittrex


class BittrexStatsProvider(StatsProvider,
                           BittrexProvider):

    def __init__(self,
                 base_currency=None,
                 quote_currency=None,
                 api=bittrex.bittrex(None, None)):

        BittrexProvider.__init__(self, base_currency, quote_currency, api)

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