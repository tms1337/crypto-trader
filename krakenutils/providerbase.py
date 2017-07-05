import krakenex


class ProviderBase:
    def __init__(self, currency="USD", crypto="ETH", api=krakenex.API()):
        self._check_currency(currency)
        self._check_crypto(crypto)

        self.currency = currency
        self.crypto = crypto

        self.k = api

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
