import logging

import time
from poloniex import Poloniex

from trading.exchange.base import CurrencyMixin, KeyLoaderMixin
from trading.util.logging import LoggableMixin


class PoloniexProvider(CurrencyMixin, LoggableMixin):
    def __init__(self,
                 api=Poloniex(),
                 pause_dt=1):

        self._check_api(api)
        self.api = api

        self.pause_dt = pause_dt

        CurrencyMixin.__init__(self)
        LoggableMixin.__init__(self, PoloniexProvider)


    def currency_mapping(self):
        mapping = {
            "ETH": "ETH",
            "BTC": "BTC",
            "DASH": "DASH",
            "XRP": "XRP",
            "USD": "USD",
            "ETC": "ETC",
            "LTC": "LTC"
        }

        return mapping

    def currency_mapping_for_balance(self):
        mapping = {
            "ETH": "ETH",
            "BTC": "BTC",
            "DASH": "DASH",
            "XRP": "XRP",
            "USD": "USD",
            "ETC": "ETC",
            "LTC": "LTC"
        }

        return mapping

    def form_pair(self):
        return "%s_%s" % (self.quote_currency,
                          self.base_currency)

    def _check_api(self, api):
        if not isinstance(api, Poloniex):
            error_message = "API object must be an instance of Poloniex"

            self.logger.error(error_message)
            raise ValueError(error_message)

    def _check_response(self, response):
        time.sleep(self.pause_dt)
        self.logger.debug("Checking response: %s" % str(response)[1:100])


class PrivatePoloniexProvider(PoloniexProvider, KeyLoaderMixin, LoggableMixin):
    def __init__(self,
                 key_uri,
                 api=Poloniex()):

        PoloniexProvider.__init__(self,
                                  api)

        KeyLoaderMixin.__init__(self, key_uri)
        self.api.key = self.key
        self.api.secret = self.secret

        LoggableMixin.__init__(self, PrivatePoloniexProvider)
