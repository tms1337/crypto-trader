from trading.exchange.base import StatsProvider
from poloniex import Poloniex
from .base import PoloniexProvider


class PoloniexStatsProvider(StatsProvider,
                            PoloniexProvider):

    def __init__(self,
                 base_currency=None,
                 quote_currency=None,
                 api=Poloniex()):

        PoloniexProvider.__init__(self,
                                  base_currency,
                                  quote_currency,
                                  api)

    def ohlc_history(self, interval=1, since=None):
        raise NotImplementedError()

    def ticker_high(self):
        ticker_response = self._ticker_price()

        price = ticker_response[self.form_pair()]["highestBid"]

        return float(price)

    def ticker_low(self):
        ticker_response = self._ticker_price()

        price = ticker_response[self.form_pair()]["lowestAsk"]

        return float(price)

    def ticker_last(self):
        ticker_response = self._ticker_price()

        price = ticker_response[self.form_pair()]["last"]

        return float(price)

    def _ticker_price(self):
        ticker_response = self.api.returnTicker()

        self._check_response(ticker_response)
        return ticker_response






