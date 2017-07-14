import krakenex

from .base import PrivateKrakenProvider
from ..base import CurrencyMixin, TradeProvider


class KrakenTradeProvider(PrivateKrakenProvider,
                          TradeProvider):
    def __init__(self, key_uri, base_currency, quote_currency, api=krakenex.API()):
        PrivateKrakenProvider.__init__(self,
                                       key_uri=key_uri,
                                       base_currency=base_currency,
                                       quote_currency=quote_currency,
                                       api=api)

    def total_balance(self):
        balance_response = self.k.query_private("Balance")
        self._check_response(balance_response)

        balance = balance_response["result"]

        return balance

    def create_buy_offer(self, volume, price=None):
        if price is None:
            self._create_market_buy_offer(volume)
        else:
            offer_response = self.k.query_private("AddOrder", {"pair": self.form_pair(),
                                                               "type": "buy",
                                                               "ordertype": "limit",
                                                               "price": str(price),
                                                               "volume": str(volume),
                                                               "trading_agreement": "agree"})
            self._check_response(offer_response)

    def create_sell_offer(self, volume, price=None):
        if price is None:
            self._create_market_sell_offer(volume)
        else:
            offer_response = self.k.query_private("AddOrder", {"pair": self.form_pair(),
                                                               "type": "sell",
                                                               "ordertype": "limit",
                                                               "price": "{0:.10f}".format(price),
                                                               "volume": "{0:.10f}".format(volume),
                                                               "trading_agreement": "agree"})

            self._check_response(offer_response)

    def _create_market_buy_offer(self, volume):
        offer_response = self.k.query_private("AddOrder", {"pair": self.form_pair(),
                                                           "type": "buy",
                                                           "ordertype": "market",
                                                           "volume": str(volume),
                                                           "trading_agreement": "agree"})
        self._check_response(offer_response)

    def _create_market_sell_offer(self, volume):
        offer_response = self.k.query_private("AddOrder", {"pair": self.form_pair(),
                                                           "type": "sell",
                                                           "ordertype": "market",
                                                           "volume": str(volume),
                                                           "trading_agreement": "agree"})
        self._check_response(offer_response)
