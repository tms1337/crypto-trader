import krakenex

from bot.exceptions.servererror import ServerError
from util.logging import LoggableMixin
from .base import KrakenProvider
from ..base import StatsProvider


class KrakenStatsProvider(StatsProvider,
                          KrakenProvider,
                          LoggableMixin):

    def __init__(self,
                 api=krakenex.API(),
                 pause_dt=1):

        KrakenProvider.__init__(self, api, pause_dt)
        LoggableMixin.__init__(self, KrakenStatsProvider)

    def ohlc_history(self, interval=1, since=None):
        parameters = {"pair": self.form_pair(),
                      "interval": interval}

        if since is not None:
            parameters["since"] = self._get_timestamp_period_before(since)

        ohlc_response = self.k.query_public("OHLC", parameters)
        self._check_response(ohlc_response)

        map_key = [k for k in ohlc_response["result"] if k != "last"][0]
        ohlcs = ohlc_response["result"][map_key]

        return ohlcs

    def ticker_high(self):
        ticker_response = self._ticker_price()
        pair_key = [k for k in ticker_response["result"]][0]

        return float(ticker_response["result"][pair_key]["b"][0])

    def ticker_low(self):
        ticker_response = self._ticker_price()
        pair_key = [k for k in ticker_response["result"]][0]

        return float(ticker_response["result"][pair_key]["a"][0])

    def ticker_last(self):
        ticker_response = self._ticker_price()
        pair_key = [k for k in ticker_response["result"]][0]

        return float(ticker_response["result"][pair_key]["c"][0])

    def _ticker_price(self):
        try:
            ticker_response = self.k.query_public("Ticker", {"pair": self.form_pair()})
        except Exception as error:
            self._handle_error(error)
        else:
            self._check_response(ticker_response)

            return ticker_response

    def _check_response(self, server_response):
        super(KrakenStatsProvider, self)._check_response(server_response)

        if not "result" in server_response:
            raise ServerError()




