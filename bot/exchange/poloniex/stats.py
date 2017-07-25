import time

from cachetools import TTLCache

from trading.exchange.base import StatsProvider
from poloniex import Poloniex

from trading.util.asserting import TypeChecker
from trading.util.logging import LoggableMixin
from .base import PoloniexProvider


class PoloniexStatsProvider(StatsProvider,
                            PoloniexProvider,
                            LoggableMixin):

    def __init__(self,
                 api=Poloniex(),
                 pause_dt=1,
                 cache_time=5):

        TypeChecker.check_one_of_types(cache_time, [float, int])
        assert 0 < cache_time
        self.cache_time = cache_time

        self.cache = TTLCache(ttl=self.cache_time, maxsize=10)

        PoloniexProvider.__init__(self, api, pause_dt)
        LoggableMixin.__init__(self, PoloniexStatsProvider)


    def ohlc_history(self, interval=1, since=None):
        raise NotImplementedError()

    def ticker_high(self):
        ticker_response = self._ticker_price()
        self._check_response(ticker_response)

        price = ticker_response[self.form_pair()]["highestBid"]

        return float(price)

    def ticker_low(self):
        ticker_response = self._ticker_price()
        self._check_response(ticker_response)

        price = ticker_response[self.form_pair()]["lowestAsk"]

        return float(price)

    def ticker_last(self):
        ticker_response = self._ticker_price()
        self._check_response(ticker_response)

        price = ticker_response[self.form_pair()]["last"]

        return float(price)

    def _ticker_price(self):
        try:
            cached_response = self.cache["ticker_price"]
        except KeyError:
            self.logger.debug("No cached response")
        else:
            self.logger.debug("Found in cache")
            return cached_response

        try:
            ticker_response = self.api.returnTicker()
        except Exception as error:
            self._handle_error(error)
        else:
            self._check_response(ticker_response)

            self.cache.update([ ("ticker_price", ticker_response) ])

            return ticker_response






