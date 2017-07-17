import logging

from poloniex import Poloniex

from trading.deciders.decision import TransactionType
from trading.exchange.base import TradeProvider
from trading.exchange.poloniex.base import PrivatePoloniexProvider


class PoloniexTradeProvider(PrivatePoloniexProvider,
                            TradeProvider):
    def __init__(self,
                 key_uri,
                 base_currency=None,
                 quote_currency=None,
                 api=Poloniex(),
                 logger_name="app"):

        PrivatePoloniexProvider.__init__(self,
                                         key_uri,
                                         base_currency,
                                         quote_currency,
                                         api)

        self.logger_name = logger_name
        self.logger = logging.getLogger(logger_name)

        TradeProvider.__init__(self, logger_name)

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
            self.logger.error("Poloniex failed with response %s" % response)
            raise RuntimeError("Trade did not go trough")

    def prepare_currencies(self, base_currency, quote_currency):
        self.set_currencies(base_currency, quote_currency)
