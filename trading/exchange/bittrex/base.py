import logging

from trading.exchange.base import CurrencyMixin
from .client import bittrex


class BittrexProvider(CurrencyMixin):
    def __init__(self,
                 base_currency=None,
                 quote_currency=None,
                 api=bittrex.bittrex(None, None),
                 logger_name="app"):

        self.api = api

        self.logger_name = logger_name
        self.logger = logging.getLogger("%s.BittrexProvider" % logger_name)

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
            "ETC": "ETC",
            "LTC": "LTC"
        }

        return currency_mapping[currency]

    def form_pair(self):
        return "%s-%s" % (self.quote_currency,
                          self.base_currency)

    def _check_response(self, server_response):
        self.logger.debug("Checking response: %s" % server_response)

        if server_response in ["INSUFFICIENT_FUNDS"]:
            error_message = "Bittrex response failure %s" % server_response

            self.logger.error(error_message)
            raise RuntimeError(error_message)


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
