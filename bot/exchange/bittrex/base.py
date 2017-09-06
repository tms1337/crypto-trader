from bot.exceptions.servererror import ServerError
from bot.exchange.base import CurrencyMixin, KeyLoaderMixin, Provider
from util.logging import LoggableMixin
from .client import bittrex


class BittrexProvider(CurrencyMixin, Provider, LoggableMixin):
    def __init__(self,
                 api=bittrex.bittrex(None, None),
                 pause_dt=1):
        self.api = api
        self.pause_dt = pause_dt

        CurrencyMixin.__init__(self)
        LoggableMixin.__init__(self, BittrexProvider)

    def currency_mapping(self):
        mapping = {
            "ETH": "ETH",
            "BTC": "BTC",
            "DASH": "DASH",
            "XRP": "XRP",
            "USD": "USDT",
            "ETC": "ETC",
            "LTC": "LTC",
            "NEO": "NEO",
            "QTUM": "QTUM",
            "LSK": "LSK"
        }

        return mapping

    def currency_mapping_for_balance(self):
        currency_mapping = {
            "ETH": "ETH",
            "BTC": "BTC",
            "DASH": "DASH",
            "XRP": "XRP",
            "USD": "USDT",
            "ETC": "ETC",
            "LTC": "LTC",
            "NEO": "NEO",
            "QTUM": "QTUM",
            "LSK": "LSK"
        }

        return currency_mapping

    def form_pair(self):
        return "%s-%s" % (self.quote_currency,
                          self.base_currency)

    def _check_response(self, server_response):
        super(BittrexProvider, self)._check_response(server_response)

        self.logger.debug("Checking response: %s" % str(server_response)[1:100])

        if server_response in ["INSUFFICIENT_FUNDS"]:
            error_message = "Bittrex response failure %s" % server_response

            self.logger.error(error_message)
            raise ServerError(error_message)

    def prepare_currencies(self, base_currency, quote_currency):
        self.set_currencies(base_currency, quote_currency)


class PrivateBittrexProvider(BittrexProvider, KeyLoaderMixin, LoggableMixin):
    def __init__(self,
                 key_uri,
                 api=bittrex.bittrex(None, None),
                 pause_dt=1):
        BittrexProvider.__init__(self,
                                 api,
                                 pause_dt)

        KeyLoaderMixin.__init__(self, key_uri)

        self.api = bittrex.bittrex(self.key,
                                   self.secret)

        LoggableMixin.__init__(self, PrivateBittrexProvider)
