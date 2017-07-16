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
        if "error" in response:
            if self.verbose >= 1:
                print("Bitfinex failed with response %s" % response)
            raise RuntimeError("Trade did not go trough")

    def prepare_currencies(self, base_currency, quote_currency):
        self.set_currencies(base_currency, quote_currency)
