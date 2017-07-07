import krakenex

from .providerbase import PrivateProviderBase


class TradeProvider(PrivateProviderBase):
    def __init__(self, key_uri, currency, crypto, api=krakenex.API()):
        super(TradeProvider, self).__init__(key_uri, currency, crypto, api)

    def total_balance(self):
        balance_response = self.k.query_private('Balance')
        self._check_response(balance_response)

        balance = balance_response["result"]

        return balance

    def create_buy_offer(self, volume, price=None):
        if price == None:
            self._create_limit_buy_offer(volume)
        else:
            self.k.query_private('AddOrder', {'pair': self._form_pair(),
                                              'type': 'buy',
                                              'ordertype': 'market',
                                              'price': str(price),
                                              'volume': str(volume)})

    def _create_limit_buy_offer(self, volume):
        self.k.query_private('AddOrder', {'pair': self._form_pair(),
                                          'type': 'buy',
                                          'ordertype': 'limit',
                                          'volume': str(volume)})
