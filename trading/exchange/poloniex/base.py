import logging

import time
from poloniex import Poloniex

from trading.exchange.base import CurrencyMixin, KeyLoaderMixin


class PoloniexProvider(CurrencyMixin):
    def __init__(self,
                 api=Poloniex(),
                 logger_name="app",
                 pause_dt=2):

        self._check_api(api)
        self.api = api

        self.logger_name = logger_name
        self.logger = logging.getLogger("%s.PoloniexProvider" % logger_name)
        self.pause_dt = pause_dt

        CurrencyMixin.__init__(self)


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


class PrivatePoloniexProvider(PoloniexProvider, KeyLoaderMixin):
    def __init__(self,
                 key_uri,
                 base_currency,
                 quote_currency,
                 api=Poloniex()):

        PoloniexProvider.__init__(self,
                                  base_currency,
                                  quote_currency,
                                  api)

        KeyLoaderMixin.__init__(self, key_uri)

        self.api.key = self.key
        self.api.secret = self.secret
