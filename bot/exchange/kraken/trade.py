import krakenex

from bot.exceptions.servererror import ServerError
from util.logging import LoggableMixin
from .base import PrivateKrakenProvider
from ..base import TradeProvider


class KrakenTradeProvider(PrivateKrakenProvider,
                          TradeProvider,
                          LoggableMixin):
    def __init__(self,
                 key_uri,
                 api=krakenex.API(),
                 pause_dt=1):

        PrivateKrakenProvider.__init__(self,
                                       key_uri=key_uri,
                                       api=api,
                                       pause_dt=pause_dt)

        LoggableMixin.__init__(self, KrakenTradeProvider)

    def total_balance(self, currency=None):
        try:
            balance_response = self.k.query_private("Balance")
        except Exception as error:
            self._handle_error(error)
        else:
            self._check_response(balance_response)

            balance = balance_response["result"]

            if not currency is None:
                return float(balance[self.map_currency_balance(currency)])
            else:
                return {self.inverse_map_currency(k):float(balance[k]) for k in balance if k in ["XETH", "XXBT", "XICN", "XXLM"]}

    def create_buy_offer(self, volume, price=None):
        if price is None:
            return self._create_market_buy_offer(volume)
        else:
            try:
                offer_response = self.k.query_private("AddOrder", {"pair": "XETHXXBT",
                                                                   "type": "buy",
                                                                   "ordertype": "limit",
                                                                   "price": "{0:.10f}".format(price),
                                                                   "volume": "{0:.10f}".format(volume),
                                                                   "trading_agreement": "agree"})
            except Exception as error:
                self._handle_error(error)
            else:
                self._check_response(offer_response)

                # TODO: check if multiple :(
                return offer_response["result"]["txid"][0]

    def create_sell_offer(self, volume, price=None):
        if price is None:
            return self._create_market_sell_offer(volume)
        else:
            try:
                offer_response = self.k.query_private("AddOrder", {"pair": self.form_pair(),
                                                                   "type": "sell",
                                                                   "ordertype": "limit",
                                                                   "price": "{0:.10f}".format(price),
                                                                   "volume": "{0:.10f}".format(volume),
                                                                   "trading_agreement": "agree"})
            except Exception as error:
                self._handle_error(error)
            else:
                self._check_response(offer_response)

                return offer_response["result"]["txid"][0]

    def cancel_offer(self, offer_id):
        try:
            cancel_response = self.k.query_private("CancelOrder", {"txid": offer_id})
        except Exception as error:
            self._handle_error(error)
        else:
            self._check_response(cancel_response)

    def _create_market_buy_offer(self, volume):
        try:
            offer_response = self.k.query_private("AddOrder", {"pair": self.form_pair(),
                                                               "type": "buy",
                                                               "ordertype": "market",
                                                               "volume": "{0:.10f}".format(volume),
                                                               "trading_agreement": "agree"})
        except Exception as error:
            self._handle_error(error)
        else:
            self._check_response(offer_response)

            return offer_response["result"]["txid"][0]

    def _create_market_sell_offer(self, volume):
        try:
            offer_response = self.k.query_private("AddOrder", {"pair": self.form_pair(),
                                                               "type": "sell",
                                                               "ordertype": "market",
                                                               "volume": "{0:.10f}".format(volume),
                                                               "trading_agreement": "agree"})
        except Exception as error:
            self._handle_error(error)
        else:
            self._check_response(offer_response)

            return offer_response["result"]["txid"][0]

    def _check_response(self, server_response):
        super(KrakenTradeProvider, self)._check_response(server_response)

        if "result" not in server_response:
            raise ServerError(str(server_response))
        elif "txid" not in server_response["result"]:
            raise ServerError(str(server_response))
        elif len(server_response["result"]["txid"]) == 0:
            raise ServerError(str(server_response))





