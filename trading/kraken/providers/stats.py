import krakenex
from .providerbase import ProviderBase


class StatsProvider(ProviderBase):
    def __init__(self, base_currency, quote_currency, api=krakenex.API()):
        super(StatsProvider, self).__init__(base_currency, quote_currency, api)

    def last_ohlc(self, period=10):
        parameters = {"pair": self._form_pair(), "since": self.get_timestamp(period)}
        ohlc_response = self.k.query_public("OHLC", parameters)

        self._check_response(ohlc_response)

        last_ohlc = ohlc_response["result"][self._form_pair()][-1]

        return last_ohlc
