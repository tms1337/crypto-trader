from trading.exchange.base import CurrencyMixin
from .client import bittrex


class BittrexProvider(CurrencyMixin):
    def __init__(self,
                 base_currency,
                 quote_currency,
                 api=bittrex.bittrex(None, None)):
        self.api = api

        CurrencyMixin.__init__(self,
                               base_currency,
                               quote_currency)

    def map_currency(self, currency):
        currency_mapping = {
            "ETH": "ETH",
            "BTC": "BTC",
            "DASH": "DASH",
            "XRP": "XRP",
            "USD": "USD",
        }

        return currency_mapping[currency]

    def form_pair(self):
        return "%s-%s" % (self.quote_currency,
                          self.base_currency)

    @staticmethod
    def _check_response(server_response):
        pass


class PrivateBittrexProvider(BittrexProvider):
    def __init__(self,
                 key_uri,
                 base_currency,
                 quote_currency,
                 api=bittrex.bittrex(None, None)):
        BittrexProvider.__init__(self,
                                 base_currency,
                                 quote_currency,
                                 api)

        self.key_uri = key_uri
        self._load_key()
        self._load_secret()

        self.api = bittrex.bittrex(self.key,
                                   self.secret)

    # TODO: key loader superclass
    def _load_key(self):
        content = self._get_key_file_content()
        self.key = content[0]

    def _load_secret(self):
        content = self._get_key_file_content()
        self.secret = content[1]

    def _get_key_file_content(self):
        with open(self.key_uri) as f:
            content = f.readlines()
        content = [x.strip() for x in content]
        return content
