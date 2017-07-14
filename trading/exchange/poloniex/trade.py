from poloniex import Poloniex

from trading.exchange.base import TradeProvider
from trading.exchange.poloniex.base import PrivatePoloniexProvider


class PoloniexTradeProvider(PrivatePoloniexProvider,
                            TradeProvider):

    def __init__(self, key_uri,
                 base_currency,
                 quote_currency,
                 api=Poloniex(),
                 verbose=1):
        PrivatePoloniexProvider.__init__(self,
                                key_uri,
                                base_currency,
                                quote_currency,
                                api)
        TradeProvider.__init__(self, verbose)

    def create_buy_offer(self, volume, price=None):
        buy_response = self.api.buy(self.form_pair(),
                                    price,
                                    volume,
                                    orderType="fillOrKill")

        self._check_response(buy_response)

    def total_balance(self):
        balance = self.api.returnBalances()

        return balance

    def create_sell_offer(self, volume, price=None):
        sell_response = self.api.sell(self.form_pair(),
                                      price,
                                      volume,
                                      orderType="fillOrKill")

        self._check_response(sell_response)

    @staticmethod
    def _check_response(response):
        if "orderNumber" not in response:
            raise RuntimeError("Trade did not go trough")

    def prepare_currencies(self, base_currency, quote_currency):
        self.set_currencies(base_currency, quote_currency)

