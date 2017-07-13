from poloniex import Poloniex


class PoloniexProvider:
    def __init__(self,
                 base_currency,
                 quote_currency,
                 api=Poloniex()):

        self._check_base_currency(base_currency)
        self._check_quote_currency(quote_currency)
        self._check_api(api)
        self.api = api

    @staticmethod
    def _check_api(api):
        if not isinstance(api, Poloniex):
            raise ValueError("API object must be an instance of Poloniex")

    @staticmethod
    def _check_base_currency(base_currency):
        if not isinstance(base_currency, str):
            raise ValueError("Base currency must be string")

    @staticmethod
    def _check_quote_currency(quote_currency):
        if not isinstance(quote_currency, str):
            raise ValueError("Quote currency must be string")


class PrivatePoloniexProvider(PoloniexProvider):
    def __init__(self,
                 key_uri,
                 base_currency,
                 quote_currency,
                 api=Poloniex()):
        PoloniexProvider.__init__(self,
                                  base_currency,
                                  quote_currency,
                                  api)
        self.key_uri = key_uri

        self._load_key()
        self._load_secret()

        self.api.key = self.key
        self.api.secret = self.secret

    def _load_key(self):
        self.key = None

    def _load_secret(self):
        self.secret = None
