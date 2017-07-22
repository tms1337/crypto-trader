from trading.util.logging import LoggableMixin
from .base import BittrexProvider
from ..base import CurrencyMixin, StatsProvider
from .client import bittrex


class BittrexStatsProvider(StatsProvider,
                           BittrexProvider,
                           LoggableMixin):

    def __init__(self,
                 api=bittrex.bittrex(None, None),
                 pause_dt=1):

        BittrexProvider.__init__(self, api, pause_dt)
        LoggableMixin.__init__(self, BittrexStatsProvider)

        self.cached_ticker_last = None
        self.cache_time = None

    def ohlc_history(self, interval=1, since=None):
        raise NotImplementedError()

    def ticker_high(self):
        try:
            ticker_response = self.api.getticker(market=self.form_pair())
        except Exception as error:
            self._handle_error(error)
        else:
            self._check_response(ticker_response)

            return ticker_response["Ask"]

    def ticker_low(self):
        try:
            ticker_response = self.api.getticker(market=self.form_pair())
        except Exception as error:
            self._handle_error(error)
        else:
            self._check_response(ticker_response)

            return ticker_response["Bid"]

    def ticker_last(self):
        try:
            ticker_response = self.api.getticker(market=self.form_pair())
        except Exception as error:
            self._handle_error(error)
        else:
            self._check_response(ticker_response)

            return ticker_response["Last"]