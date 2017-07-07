import krakenex
from .base import Provider


class StatsProvider(Provider):
    def __init__(self, base_currency, quote_currency, api=krakenex.API()):
        super(StatsProvider, self).__init__(base_currency, quote_currency, api)

    def ohlc_history(self):
        period = None
        parameters = {"pair": self._form_pair()}

        if period is not None:
            parameters["since"] = self._get_timestamp_period_before(period)

        ohlc_response = self.k.query_public("OHLC", parameters)
        self._check_response(ohlc_response)

        map_key = [k for k in ohlc_response["result"] if k != "last"][0]
        ohlcs = ohlc_response["result"][map_key]

        return ohlcs

    def last_ohlc(self):
        history = self.ohlc_history()

        last_ohlc = history[-1]

        return last_ohlc

    def last_open(self):
        return self.last_ohlc()[1]

    def last_high(self):
        return self.last_ohlc()[2]

    def last_low(self):
        return self.last_ohlc()[3]

    def last_close(self):
        return self.last_ohlc()[4]
