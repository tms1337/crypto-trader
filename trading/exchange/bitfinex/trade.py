from trading.deciders.decision import TransactionType
from trading.exchange.base import TradeProvider
from trading.exchange.bitfinex.base import PrivateBitfinexProvider
import FinexAPI.FinexAPI as finex


class BitfinexTradeProvider(PrivateBitfinexProvider,
                            TradeProvider):
    def __init__(self, key_uri,
                 base_currency,
                 quote_currency,
                 api=finex,
                 verbose=1):
        PrivateBitfinexProvider.__init__(self,
                                         key_uri,
                                         base_currency,
                                         quote_currency,
                                         api)
        TradeProvider.__init__(self, verbose)

    def total_balance(self):
        balance_response = self.api.balances()
        self._check_response(balance_response)

        return balance_response

    def create_buy_offer(self, volume, price=None):
        pass

    def create_sell_offer(self, volume, price=None):
        pass
