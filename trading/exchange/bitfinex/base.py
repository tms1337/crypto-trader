from trading.exchange.base import CurrencyMixin
import FinexAPI


class BitfinexProvider(CurrencyMixin):
    def __init__(self,
                 base_currency,
                 quote_currency,
                 api=None):

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
        }

        return currency_mapping[currency]


