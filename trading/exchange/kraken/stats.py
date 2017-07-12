import krakenex
from .base import KrakenProvider
from ..base import CurrencyMixin, StatsProvider


class KrakenStatsProvider(CurrencyMixin,
                          StatsProvider,
                          KrakenProvider):

    def __init__(self, base_currency, quote_currency, api=krakenex.API()):
        CurrencyMixin.__init__(self, base_currency, quote_currency)
        KrakenProvider.__init__(self, base_currency, quote_currency, api)

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

    def last_ohlc(self, interval=1):
        history = self.ohlc_history(interval)

        last_ohlc = history[-1]

        return last_ohlc

    def last_open(self, interval=1):
        return float(self.last_ohlc(interval)[1])

    def last_high(self, interval=1):
        return float(self.last_ohlc(interval)[2])

    def last_low(self, interval=1):
        return float(self.last_ohlc(interval)[3])

    def last_close(self, interval=1):
        return float(self.last_ohlc(interval)[4])
