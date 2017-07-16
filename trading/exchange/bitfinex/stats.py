from trading.exchange.base import StatsProvider
from trading.exchange.bitfinex.base import BitfinexProvider
import FinexAPI.FinexAPI as finex



class BitfinexStatsProvider(BitfinexProvider,
                            StatsProvider):

    def ticker_last(self):
        ticker_response = finex.ticker(symbol=self.form_pair())
        self._check_response(ticker_response)

        return ticker_response["last_price"]

    def ticker_low(self):
        ticker_response = finex.ticker(symbol=self.form_pair())
        self._check_response(ticker_response)

        return ticker_response["low"]

    def ticker_high(self):
        ticker_response = finex.ticker(symbol=self.form_pair())
        self._check_response(ticker_response)

        return ticker_response["high"]

    def last_high(self, interval=1):
        return super().last_high(interval)

    def ohlc_history(self, interval=1, since=None):
        super().ohlc_history(interval, since)

    def last_close(self, interval=1):
        return super().last_close(interval)

    def last_ohlc(self, interval=1):
        return super().last_ohlc(interval)

    def last_open(self, interval=1):
        return super().last_open(interval)

    def last_low(self, interval=1):
        return super().last_low(interval)