import krakenex
from trading.kraken.providers.base import PrivateProvider


class TradeProviderMock(PrivateProvider):
    def __init__(self,
                 key_uri,
                 base_currency,
                 quote_currency,
                 initial_balance=100):

        api = krakenex.API()
        super(TradeProviderMock, self).__init__(key_uri,
                                                base_currency,
                                                quote_currency,
                                                api)

        self.balance = []
        self.init_balance()

    def init_balance(self):
        self.balance[self.base_currency] = 100
        self.balance[self.quote_currency] = 100

    def total_balance(self):
        pass

    def create_buy_offer(self, volume, price=None):
        pass

    def create_sell_offer(self, volume, price=None):
        pass

    def create_bulk_offers(self, offers):
        pass

    def _create_market_buy_offer(self, volume):
        pass

    def _create_market_sell_offer(self, volume):
        pass