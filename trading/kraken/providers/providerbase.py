import krakenex


class ProviderBase:
    def __init__(self,
                 base_currency,
                 quote_currency,
                 api=krakenex.API()):

        self.k = api

        self._check_currency(base_currency)
        self._check_currency(quote_currency)

        self.base_currency = base_currency
        self.quote_currency = quote_currency

    def _check_currency(self, currency):
        assets_response = self.k.query_public("Assets")
        self._check_response(assets_response)

        currencies = [ k for k in assets_response["result"] ]
        alt_currencies = [ assets_response["result"][k]["altname"] for k in assets_response["result"] ]

        currencies.extend(alt_currencies)

        if not currency in currencies:
            raise ValueError("Currency must be one of %s", str(currencies))

    def _form_pair(self):
        return "%s%s" % (self.base_currency, self.quote_currency)

    def _check_response(self, server_response):
        if "error" not in server_response:
            raise ValueError("Server responded with invalid response")

        if len(server_response["error"]) != 0:
            raise RuntimeError("Server responded with error")

    def get_timestamp(self, period):
        time_response = self.k.query_public("Time")
        self._check_response(time_response)

        time_minus_period = int(time_response["result"]["unixtime"]) - period

        return time_minus_period

class PrivateProviderBase(ProviderBase):
    def __init__(self, key_uri, base_currency, quote_currency, api=krakenex.API()):
        super(PrivateProviderBase, self).__init__(base_currency, quote_currency, api)
        self.k.load_key(key_uri)
