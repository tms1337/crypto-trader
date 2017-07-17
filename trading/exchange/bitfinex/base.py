import logging

from trading.exchange.base import CurrencyMixin
import FinexAPI.FinexAPI as finex


class BitfinexProvider(CurrencyMixin):
    def __init__(self,
                 base_currency,
                 quote_currency,
                 api=finex,
                 logger_name="app"):
        self.api = api

        self.logger_name = logger_name
        self.logger = logging.getLogger("%s.BitfinexProvider" % logger_name)

        CurrencyMixin.__init__(self,
                               base_currency,
                               quote_currency)

    def map_currency(self, currency):
        currency_mapping = {
            "ETH": "eth",
            "BTC": "btc",
            "DASH": "dash",
            "XRP": "xrp",
            "USD": "USD",
            "LTC": "LTC"
        }

        return currency_mapping[currency]

    def form_pair(self):
        return CurrencyMixin.form_pair(self)

    def _check_response(self, response):
        self.logger.debug("Checking response: %s" % response)

        if not isinstance(response, dict) and not isinstance(response, list):
            error_message = "Error during connecting to Bitfinex"

            self.logger.error("%s\n\t%s" % (error_message, response))
            raise RuntimeError(error_message)


class PrivateBitfinexProvider(BitfinexProvider):
    def __init__(self, key_uri, base_currency, quote_currency, api=finex):
        BitfinexProvider.__init__(self,
                                  base_currency,
                                  quote_currency,
                                  api)
        self.api.load_keys(key_uri)
