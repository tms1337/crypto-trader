import krakenex

from .providerbase import PrivateProviderBase


class TradeProvider(PrivateProviderBase):
    def __init__(self, key_uri, base_currency, quote_currency, api=krakenex.API()):
        super(TradeProvider, self).__init__(key_uri, base_currency, quote_currency, api)

    def total_balance(self):
        balance_response = self.k.query_private("Balance")
        self._check_response(balance_response)

        balance = balance_response["result"]

        return balance

    def create_buy_offer(self, volume, price=None):
        if price is None:
            self._create_market_buy_offer(volume)
        else:
            offer_response = self.k.query_private("AddOrder", {"pair": self._form_pair(),
                                                               "type": "buy",
                                                               "ordertype": "limit",
                                                               "price": str(price),
                                                               "volume": str(volume),
                                                               "trading_agreement": "agree"})
            print(offer_response)

            self._check_response(offer_response)

    def create_sell_offer(self, volume, price=None):
        if price is None:
            self._create_market_sell_offer(volume)
        else:
            offer_response = self.k.query_private("AddOrder", {"pair": self._form_pair(),
                                                               "type": "sell",
                                                               "ordertype": "limit",
                                                               "price": str(price),
                                                               "volume": str(volume),
                                                               "trading_agreement": "agree"})

            print(offer_response)
            self._check_response(offer_response)

    def _create_market_buy_offer(self, volume):
        offer_response = self.k.query_private("AddOrder", {"pair": self._form_pair(),
                                                           "type": "buy",
                                                           "ordertype": "market",
                                                           "volume": str(volume),
                                                           "trading_agreement": "agree"})
        print(offer_response)
        self._check_response(offer_response)

    def _create_market_sell_offer(self, volume):
        offer_response = self.k.query_private("AddOrder", {"pair": self._form_pair(),
                                                           "type": "sell",
                                                           "ordertype": "market",
                                                           "volume": str(volume),
                                                           "trading_agreement": "agree"})
        print(offer_response)
        self._check_response(offer_response)
