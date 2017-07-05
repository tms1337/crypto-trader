import krakenex


class StatsProvider:
    def __init__(self, currency="USD", crypto="ETH", api=krakenex.API()):
        self._check_currency(currency)
        self._check_crypto(crypto)

        self.currency = currency
        self.crypto = crypto

        self.k = api

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

    def _check_currency(self, currency):
        currencies = ["USD", "EUR"]
        if not currency in currencies:
            raise ValueError("Currency must be one of %s", str(currencies))

    def _check_crypto(self, crypto):
        cryptos = ["BTC", "ETH", "XRP"]
        if not crypto in cryptos:
            raise ValueError("Cryptocurrency must be one of %s", str(cryptos))

    def _form_pair(self):
        return "X%sZ%s" % (self.crypto, self.currency)

    def _check_response(self, server_response):
        if "error" not in server_response:
            raise ValueError("Server responded with invalid response")

        if len(server_response["error"]) != 0:
            raise RuntimeError("Server responded with error")
