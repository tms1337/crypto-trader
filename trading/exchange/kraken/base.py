import krakenex


class KrakenProvider:
    def __init__(self,
                 base_currency,
                 quote_currency,
                 api=krakenex.API()):

        self.k = api

        self._check_currency(base_currency)
        self._check_currency(quote_currency)

    def _check_currency(self, currency):
        assets_response = self.k.query_public("Assets")
        self._check_response(assets_response)

        results = assets_response["result"]
        currencies = [k for k in results]
        alt_currencies = [results[k]["altname"]
                          for k in
                          results]

        currencies.extend(alt_currencies)

        if not currency in currencies:
            raise ValueError("Currency must be one of %s", str(currencies))

    @staticmethod
    def _check_response(server_response):
        if "error" not in server_response:
            raise ValueError("Server responded with invalid response")

        if len(server_response["error"]) != 0:
            raise RuntimeError("Server responded with error")

    def _get_timestamp_period_before(self, period):
        time_response = self.k.query_public("Time")
        self._check_response(time_response)

        time_minus_period = int(time_response["result"]["unixtime"]) - period

        return time_minus_period


class PrivateKrakenProvider(KrakenProvider):
    def __init__(self, key_uri, base_currency, quote_currency, api=krakenex.API()):
        super(PrivateKrakenProvider, self).__init__(base_currency, quote_currency, api)
        self.k.load_key(key_uri)
