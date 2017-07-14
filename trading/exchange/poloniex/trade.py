from poloniex import Poloniex

from trading.deciders.decision import TransactionType
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

    def execute_single_decision(self, decision):
        self.prepare_currencies(decision.base_currency,
                                decision.quote_currency)

        if decision.transaction_type == TransactionType.BUY:
            self.create_buy_offer(decision.volume, decision.price)
        elif decision.transaction_type == TransactionType.SELL:
            self.create_sell_offer(decision.volume, decision.price)

    def total_balance(self):
        balance = self.api.returnBalances()

        return balance

    def create_buy_offer(self, volume, price=None):
        buy_response = self.api.buy(self.form_pair(),
                                    price,
                                    volume)

        self._check_response(buy_response)

    def create_sell_offer(self, volume, price=None):
        sell_response = self.api.sell(self.form_pair(),
                                      price,
                                      volume)

        self._check_response(sell_response)

    def _check_response(self, response):
        if "orderNumber" not in response:
            if self.verbose >= 1:
                print("Poloniex failed with response %s" % response)
            raise RuntimeError("Trade did not go trough")

    def prepare_currencies(self, base_currency, quote_currency):
        self.set_currencies(base_currency, quote_currency)

