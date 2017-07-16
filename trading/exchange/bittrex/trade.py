from .client import bittrex

from .base import PrivateBittrexProvider
from ..base import CurrencyMixin, TradeProvider


class BittrexTradeProvider(PrivateBittrexProvider,
                          TradeProvider):
    def __init__(self,
                 key_uri,
                 base_currency,
                 quote_currency,
                 api=bittrex.bittrex(None, None)):

        PrivateBittrexProvider.__init__(self,
                                        key_uri=key_uri,
                                        base_currency=base_currency,
                                        quote_currency=quote_currency,
                                        api=api)

    def total_balance(self):
        balance_response = self.api.getbalances()
        self._check_response(balance_response)

        return balance_response

    def create_buy_offer(self, volume, price=None):
        pass

    def create_sell_offer(self, volume, price=None):
        pass

    def prepare_currencies(self, base_currency, quote_currency):
        self.set_currencies(base_currency, quote_currency)
