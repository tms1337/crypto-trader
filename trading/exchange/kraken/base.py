import krakenex

from trading.exchange.base import CurrencyMixin


class KrakenProvider(CurrencyMixin):
    def __init__(self,
                 base_currency,
                 quote_currency,
                 api=krakenex.API()):

        self.k = api

        CurrencyMixin.__init__(self,
                               base_currency,
                               quote_currency)

    def map_currency(self, currency):
        currency_mapping = {
            "ETH": "ETH",
            "BTC": "XBT",
            "DASH": "DASH",
            "XRP": "XRP",
            "USD": "USD",
            "ETC": "ETC",
            "LTC": "LTC"
        }

        return currency_mapping[currency]

    @staticmethod
    def _check_response(server_response):
        if "error" not in server_response:
            raise ValueError("Server responded with invalid response")

        if len(server_response["error"]) != 0:
            raise RuntimeError("Server responded with error %s" % server_response["error"])

    def _get_timestamp_period_before(self, period):
        time_response = self.k.query_public("Time")
        self._check_response(time_response)

        time_minus_period = int(time_response["result"]["unixtime"]) - period

        return time_minus_period


class PrivateKrakenProvider(KrakenProvider):
    def __init__(self, key_uri, base_currency, quote_currency, api=krakenex.API()):
        super(PrivateKrakenProvider, self).__init__(base_currency, quote_currency, api)
        self.k.load_key(key_uri)
