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
                 pause_dt=1):
        PrivateBitfinexProvider.__init__(self,
                                         key_uri,
                                         api,
                                         pause_dt)
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
        try:
            balance_response = self.api.balances()
        except Exception as error:
            self._handle_error(error)
        else:
            self._check_response(balance_response)

            balance = {b["currency"]:float(b["amount"])
                       for b in balance_response if b["type"] == "exchange"}

            if not currency is None:
                return balance[self.currency_mapping_for_balance(currency)]
            else:
                return {self.inverse_map_currency(b):balance[b] for b in balance}

    def create_buy_offer(self, volume, price=None):
        try:
            offer_response = self.api.place_order(amount=str(volume),
                                                  ord_type="exchange limit",
                                                  symbol=self.form_pair(),
                                                  price=str(price),
                                                  side="buy")
        except Exception as error:
            self._handle_error(error)
        else:
            self._check_response(offer_response)

            return offer_response["order_id"]

    def create_sell_offer(self, volume, price=None):
        try:
            offer_response = self.api.place_order(amount=str(volume),
                                                  ord_type="exchange limit",
                                                  symbol=self.form_pair(),
                                                  price=str(price),
                                                  side="sell")
        except Exception as error:
            self._handle_error(error)
        else:
            self._check_response(offer_response)

            return offer_response["order_id"]

    def cancel_offer(self, offer_id):
        try:
            cancel_response = self.api.delete_order(offer_id)
        except Exception as error:
            self._handle_error(error)
        else:
            self._check_response(cancel_response)
