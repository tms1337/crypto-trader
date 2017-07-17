import logging

from poloniex import Poloniex

from trading.exchange.base import CurrencyMixin


class PoloniexProvider(CurrencyMixin):
    def __init__(self,
                 base_currency,
                 quote_currency,
                 logger_name="app",
                 api=Poloniex()):
        self._check_api(api)
        self.api = api

        self.logger_name = logger_name
        self.logger = logging.getLogger("%s.PoloniexProvider" % logger_name)

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

    def form_pair(self):
        return "%s_%s" % (self.quote_currency,
                          self.base_currency)

    def _check_api(self, api):
        if not isinstance(api, Poloniex):
            error_message = "API object must be an instance of Poloniex"

            self.logger.error(error_message)
            raise ValueError(error_message)

    def _check_response(self, response):
        self.logger.debug("Checking response: %s" % response)


class PrivatePoloniexProvider(PoloniexProvider):
    def __init__(self,
                 key_uri,
                 base_currency,
                 quote_currency,
                 api=Poloniex()):
        PoloniexProvider.__init__(self,
                                  base_currency,
                                  quote_currency,
                                  api)
        self.key_uri = key_uri

        self._load_key()
        self._load_secret()

        self.api.key = self.key
        self.api.secret = self.secret

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
