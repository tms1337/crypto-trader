from trading.strategy.decision import OfferType
from trading.exchange.base import TradeProvider
from trading.exchange.bitfinex.base import PrivateBitfinexProvider
import FinexAPI.FinexAPI as finex

from trading.util.logging import LoggableMixin


class BitfinexTradeProvider(PrivateBitfinexProvider,
                            TradeProvider,
                            LoggableMixin):
    def __init__(self,
                 key_uri,
                 api=finex,
                 verbose=1):
        PrivateBitfinexProvider.__init__(self,
                                         key_uri,
                                         api)
        TradeProvider.__init__(self)
        LoggableMixin.__init__(self, BitfinexTradeProvider)

    def currency_mapping_for_balance(self):
        mapping = {
            "BTC": "btc",
            "ETH": "eth",
            "LTC": "ltc",
            "USD": "usd"
        }

        return mapping

    def inverse_map_currency(self, currency):
        mapping = {
            "eth": "ETH",
            "btc": "BTC",
            "ltc": "LTC",
            "usd": "USD",
            "dsh": "DASH"
        }

        return mapping

    def total_balance(self, currency=None):
        balance_response = self.api.balances()
        self._check_response(balance_response)

        balance = {b["currency"]:float(b["amount"])
                   for b in balance_response if b["type"] == "exchange"}

        if not currency is None:
            return balance[self.currency_mapping_for_balance(currency)]
        else:
            return {self.inverse_map_currency(b):balance[b] for b in balance}

    def create_buy_offer(self, volume, price=None):
        offer_response = self.api.place_order(amount=str(volume),
                                              ord_type="exchange limit",
                                              symbol=self.form_pair(),
                                              price=str(price),
                                              side="buy")
        self._check_response(offer_response)

        return offer_response["order_id"]

    def create_sell_offer(self, volume, price=None):
        offer_response = self.api.place_order(amount=str(volume),
                                              ord_type="exchange limit",
                                              symbol=self.form_pair(),
                                              price=str(price),
                                              side="sell")
        self._check_response(offer_response)

        return offer_response["order_id"]

    def cancel_offer(self, offer_id):
        cancel_response = self.api.delete_order(offer_id)

        self._check_response(cancel_response)
