import logging

import time

from trading.exchange.base import CurrencyMixin, Provider
import FinexAPI.FinexAPI as finex

from trading.util.logging import LoggableMixin


class BitfinexProvider(CurrencyMixin, Provider, LoggableMixin):
    def __init__(self,
                 api=finex,
                 pause_dt=1):

        self.api = api
        self.pause_dt = pause_dt

        CurrencyMixin.__init__(self)
        LoggableMixin.__init__(self, BitfinexProvider)

    def currency_mapping(self):
        mapping = {
            "ETH": "eth",
            "BTC": "btc",
            "DASH": "dsh",
            "XRP": "xrp",
            "USD": "usd",
            "LTC": "ltc"
        }

        return mapping

    def currency_mapping_for_balance(self):
        mapping = {
            "ETH": "eth",
            "BTC": "btc",
            "DASH": "dsh",
            "XRP": "xrp",
            "USD": "usd",
            "LTC": "ltc"
        }

        return mapping

    def form_pair(self):
        return CurrencyMixin.form_pair(self)

    def _check_response(self, response):
        time.sleep(self.pause_dt)
        self.logger.debug("Checking response: %s" % str(response)[1:100])

        if not isinstance(response, dict) and not isinstance(response, list):
            error_message = "Error during connecting to Bitfinex"

            self.logger.error("%s\n\t%s" % (error_message, response))
            raise RuntimeError(error_message)


class PrivateBitfinexProvider(BitfinexProvider, LoggableMixin):
    def __init__(self,
                 key_uri,
                 api=finex):

        BitfinexProvider.__init__(self,
                                  api)
        self.api.load_keys(key_uri)
        LoggableMixin.__init__(self, PrivateBitfinexProvider)

    def prepare_currencies(self, base_currency, quote_currency):
        self.set_currencies(base_currency, quote_currency)
