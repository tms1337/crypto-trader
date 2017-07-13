from poloniex import Poloniex


class PoloniexProvider:
    def __init__(self,
                 base_currency,
                 quote_currency,
                 api=Poloniex()):

        self.api = api

class PrivatePoloniexProvider(PoloniexProvider):
    def __init__(self,
                 key_uri,
                 base_currency,
                 quote_currency,
                 api=Poloniex()):

        PoloniexProvider.__init__(self, base_currency, quote_currency, api)
        self.key_uri = key_uri
