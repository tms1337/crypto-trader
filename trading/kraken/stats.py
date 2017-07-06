import krakenex
from .providerbase import ProviderBase


class StatsProvider(ProviderBase):
    def __init__(self, currency, crypto, api=krakenex.API()):
        super(StatsProvider, self).__init__(currency, crypto, api)

    def average_price(self, period_seconds=None):
        prices = self.price_history(period_seconds)

        return sum(prices) / len(prices)

    def price_history(self, period_seconds=None):
        spreads = self.spread_history(period_seconds)
        mean_values = [0.5 * (p[0] + p[1]) for p in spreads]

        return mean_values

    def spread_history(self, period_seconds=None):
        parameters = {"pair": self._form_pair()}
        if period_seconds is not None:
            server_time_response = self.k.query_public("Time")

            self._check_response(server_time_response)

            server_time = server_time_response["result"]["unixtime"]
            since = server_time - (period_seconds + 1)
            parameters["since"] = since

        trades_response = self.k.query_public("Spread", parameters)
        self._check_response(trades_response)

        all_spreads = trades_response["result"][self._form_pair()]

        return [(float(s[1]), float(s[2])) for s in all_spreads]

    def last_price(self):
        prices = self.price_history()

        if len(prices) == 0:
            raise ValueError("Server responded with empty response")

        return prices[-1]

    def last_OHLC(self):
        pass


