import logging

import krakenex
import time

from trading.exchange.base import CurrencyMixin


class KrakenProvider(CurrencyMixin):
    def __init__(self,
                 api=krakenex.API(),
                 logger_name="app",
                 pause_dt=2):

        self.k = api
        self.pause_dt = pause_dt

        self.logger_name = logger_name
        self.logger = logging.getLogger("%s.KrakenProvider" % logger_name)

        CurrencyMixin.__init__(self)

    def currency_mapping(self):
        mapping = {
            "ETH": "ETH",
            "BTC": "XBT",
            "DASH": "DASH",
            "XRP": "XRP",
            "USD": "USD",
            "ETC": "ETC",
            "LTC": "LTC",
            "ICN": "ICN",
            "XLM": "XLM"
        }

        return mapping

    def currency_mapping_for_balance(self, currency):
        currency_mapping = {
            "ETH": "XETH",
            "BTC": "XXBT",
            "DASH": "DASH",
            "XRP": "XXRP",
            "USD": "ZUSD",
            "ETC": "XETC",
            "LTC": "XLTC",
            "ICN": "XICN",
            "XLM": "XXLM"
        }

        return currency_mapping[currency]

    def _check_response(self, server_response):
        time.sleep(self.pause_dt)

        self.k = krakenex.API()

        self.logger.debug("Checking response: %s" % str(server_response)[1:100])

        if "error" not in server_response:
            error_message = "Server responded with invalid response"

            self.logger.error("%s\n\t%s" % (error_message, server_response))
            raise ValueError(error_message)

        if len(server_response["error"]) != 0:
            error_message = "Server responded with error %s" % server_response["error"]

            self.logger.error(error_message)
            raise RuntimeError(error_message)

    def _get_timestamp_period_before(self, period):
        time_response = self.k.query_public("Time")
        self._check_response(time_response)

        time_minus_period = int(time_response["result"]["unixtime"]) - period

        return time_minus_period


class PrivateKrakenProvider(KrakenProvider):
    def __init__(self, key_uri, base_currency, quote_currency, api=krakenex.API()):
        super(PrivateKrakenProvider, self).__init__(base_currency, quote_currency, api)
        self.key_uri = key_uri
        self.k.load_key(key_uri)

    def _check_response(self, server_response):
        KrakenProvider._check_response(self, server_response)
        self.k.load_key(self.key_uri)
