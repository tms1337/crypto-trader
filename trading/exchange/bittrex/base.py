import logging

import time

from trading.exchange.base import CurrencyMixin, KeyLoaderMixin, Provider
from .client import bittrex


class BittrexProvider(CurrencyMixin, Provider):
    def __init__(self,
                 base_currency=None,
                 quote_currency=None,
                 api=bittrex.bittrex(None, None),
                 logger_name="app",
                 pause_dt=2):
        self.api = api
        self.pause_dt = pause_dt

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
            "USD": "USDT",
            "ETC": "ETC",
            "LTC": "LTC"
        }

        return currency_mapping[currency]

    def currency_mapping_for_balance(self, currency):
        currency_mapping = {
            "ETH": "ETH",
            "BTC": "BTC",
            "DASH": "DASH",
            "XRP": "XRP",
            "USD": "USDT",
            "ETC": "ETC",
            "LTC": "LTC"
        }

        return currency_mapping[currency]

    def form_pair(self):
        return "%s-%s" % (self.quote_currency,
                          self.base_currency)

    def _check_response(self, server_response):
        time.sleep(self.pause_dt)

        self.logger.debug("Checking response: %s" % str(server_response)[1:100])

        if server_response in ["INSUFFICIENT_FUNDS"]:
            error_message = "Bittrex response failure %s" % server_response

            self.logger.error(error_message)
            raise RuntimeError(error_message)


class PrivateBittrexProvider(BittrexProvider, KeyLoaderMixin):
    def __init__(self,
                 key_uri,
                 base_currency,
                 quote_currency,
                 api=bittrex.bittrex(None, None)):
        BittrexProvider.__init__(self,
                                 base_currency,
                                 quote_currency,
                                 api)

        KeyLoaderMixin.__init__(self, key_uri)

        self.api = bittrex.bittrex(self.key,
                                   self.secret)
