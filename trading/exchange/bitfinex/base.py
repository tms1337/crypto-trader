import logging

import time

from trading.exchange.base import CurrencyMixin
import FinexAPI.FinexAPI as finex


class BitfinexProvider(CurrencyMixin):
    def __init__(self,
                 base_currency=None,
                 quote_currency=None,
                 api=finex,
                 logger_name="app",
                 pause_dt=2):

        self.api = api
        self.pause_dt = pause_dt

        self.logger_name = logger_name
        self.logger = logging.getLogger("%s.BitfinexProvider" % logger_name)

        CurrencyMixin.__init__(self,
                               base_currency,
                               quote_currency,
                               logger_name=self.logger_name)

    def map_currency(self, currency):
        currency_mapping = {
            "ETH": "eth",
            "BTC": "btc",
            "DASH": "dash",
            "XRP": "xrp",
            "USD": "usd",
            "LTC": "ltc"
        }

        return currency_mapping[currency]

    def map_currency_balance(self, currency):
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
        return CurrencyMixin.form_pair(self)

    def _check_response(self, response):
        time.sleep(self.pause_dt)
        self.logger.debug("Checking response: %s" % str(response)[1:100])

        if not isinstance(response, dict) and not isinstance(response, list):
            error_message = "Error during connecting to Bitfinex"

            self.logger.error("%s\n\t%s" % (error_message, response))
            raise RuntimeError(error_message)


class PrivateBitfinexProvider(BitfinexProvider):
    def __init__(self,
                 key_uri,
                 base_currency=None,
                 quote_currency=None,
                 api=finex):

        BitfinexProvider.__init__(self,
                                  base_currency,
                                  quote_currency,
                                  api)
        self.api.load_keys(key_uri)

    def prepare_currencies(self, base_currency, quote_currency):
        self.set_currencies(base_currency, quote_currency)