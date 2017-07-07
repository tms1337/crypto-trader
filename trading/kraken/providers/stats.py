import krakenex
from .providerbase import ProviderBase


class StatsProvider(ProviderBase):
    def __init__(self, base_currency, quote_currency, api=krakenex.API()):
        super(StatsProvider, self).__init__(base_currency, quote_currency, api)

    def ohlc_history(self, period=None):
        parameters = {"pair": self._form_pair()}

        if period is not None:
            parameters["since"] = self._get_timestamp_period_before(period)

        ohlc_response = self.k.query_public("OHLC", parameters)
        self._check_response(ohlc_response)

        ohlcs = ohlc_response["result"][self._form_pair()]

        return ohlcs

    def last_ohlc(self, period=10):
        history = self.ohlc_history(period)

        last_ohlc = history[-1]

        return last_ohlc
