import logging

from poloniex import Poloniex

from trading.exceptions.servererror import ServerError
from trading.strategy.decision import OfferType
from trading.exchange.base import TradeProvider
from trading.exchange.poloniex.base import PrivatePoloniexProvider
from trading.util.logging import LoggableMixin


class PoloniexTradeProvider(PrivatePoloniexProvider,
                            TradeProvider,
                            LoggableMixin):
    def __init__(self,
                 key_uri,
                 api=Poloniex(),
                 pause_dt=1):

        PrivatePoloniexProvider.__init__(self,
                                         key_uri,
                                         api,
                                         pause_dt)

        TradeProvider.__init__(self)
        LoggableMixin.__init__(self, PoloniexTradeProvider)

    def total_balance(self, currency=None):
        try:
            balance = self.api.returnCompleteBalances()
        except Exception as error:
            self._handle_error(error)
        else:
            if not currency is None:
                return float(balance[currency])
            else:
                return {b:float(balance[b]["available"]) + float(balance[b]["onOrders"]) for b in balance}

    def create_buy_offer(self, volume, price=None):
        try:
            buy_response = self.api.buy(self.form_pair(),
                                        price,
                                        volume)
        except Exception as error:
            self._handle_error(error)
        else:
            self._check_response(buy_response)

            if len(buy_response["resultingTrades"]) != 0:
                return buy_response["resultingTrades"][0]["tradeID"]
            else:
                return buy_response["orderNumber"]

    def create_sell_offer(self, volume, price=None):
        try:
            sell_response = self.api.sell(self.form_pair(),
                                          price,
                                          volume)
        except Exception as error:
            self._handle_error(error)
        else:
            self._check_response(sell_response)

            return sell_response["orderNumber"]

    def cancel_offer(self, offer_id):
        try:
            cancel_response = self.api.cancelOrder(offer_id)
        except Exception as error:
            self._handle_error(error)
        else:
            self._check_response(cancel_response)

    def _check_response(self, response):
        super(PoloniexTradeProvider, self)._check_response(response)

        if "success" in response and response["success"] == 1:
            return

        if "orderNumber" not in response:
            self.logger.error("Poloniex failed with response %s" % response)
            raise ServerError("Trade did not go trough")
