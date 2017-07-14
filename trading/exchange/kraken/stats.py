import krakenex
from .base import KrakenProvider
from ..base import CurrencyMixin, StatsProvider


class KrakenStatsProvider(StatsProvider,
                          KrakenProvider):

    def __init__(self, base_currency, quote_currency, api=krakenex.API()):
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

    def ticker_price(self):
        ticker_response = self.k.query_public("Ticker", {"pair": self.form_pair()})
        self._check_response(ticker_response)

        pair_key = [k for k in ticker_response["result"]][0]

        return float(ticker_response["result"][pair_key]["c"][0])


