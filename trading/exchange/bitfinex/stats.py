from trading.exchange.base import StatsProvider
from trading.exchange.bitfinex.base import BitfinexProvider
import FinexAPI.FinexAPI as finex

from trading.util.logging import LoggableMixin


class BitfinexStatsProvider(BitfinexProvider,
                            StatsProvider,
                            LoggableMixin):
    def __init__(self,
                 api=finex,
                 pause_dt=1):

        LoggableMixin.__init__(self, BitfinexStatsProvider)
        BitfinexProvider.__init__(self, api, pause_dt)

    def ticker_last(self):
        ticker_response = self.api.ticker(symbol=self.form_pair())
        self._check_response(ticker_response)

        return float(ticker_response["last_price"])

    def ticker_low(self):
        ticker_response = self.api.ticker(symbol=self.form_pair())
        self._check_response(ticker_response)

        return float(ticker_response["low"])

    def ticker_high(self):
        ticker_response = self.api.ticker(symbol=self.form_pair())
        self._check_response(ticker_response)

        return float(ticker_response["high"])

    def ohlc_history(self, interval=1, since=None):
        raise NotImplementedError()


