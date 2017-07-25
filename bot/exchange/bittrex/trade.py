from bot.util.logging import LoggableMixin
from .client import bittrex

from .base import PrivateBittrexProvider
from ..base import CurrencyMixin, TradeProvider


class BittrexTradeProvider(PrivateBittrexProvider,
                           TradeProvider,
                           LoggableMixin):
    def __init__(self,
                 key_uri,
                 api=bittrex.bittrex(None, None),
                 pause_dt=1):
        PrivateBittrexProvider.__init__(self,
                                        key_uri=key_uri,
                                        api=api,
                                        pause_dt=pause_dt)
        LoggableMixin.__init__(self, BittrexTradeProvider)

    def total_balance(self, currency=None):
        try:
            balance_response = self.api.getbalances()
        except Exception as error:
            self._handle_error(error)
        else:
            self._check_response(balance_response)

            if not currency is None:
                currency_balance = [b for b in balance_response if b["Currency"] == self.map_currency_balance(currency)]

                if len(currency_balance) == 0:
                    return 0.0

                currency_balance = currency_balance[0]

                return float(currency_balance["Balance"])
            else:
                return {b["Currency"]: float(b["Balance"]) for b in balance_response}

    def create_buy_offer(self, volume, price=None):
        try:
            offer_response = self.api.buylimit(self.form_pair(),
                                               volume,
                                               price)
        except Exception as error:
            self._handle_error(error)
        else:
            self._check_response(offer_response)

            return offer_response["uuid"]

    def create_sell_offer(self, volume, price=None):
        try:
            offer_response = self.api.selllimit(self.form_pair(),
                                                volume,
                                                price)
        except Exception as error:
            self._handle_error(error)
        else:
            self._check_response(offer_response)

            return offer_response["uuid"]

    def cancel_offer(self, offer_id):
        try:
            cancel_response = self.api.cancel(offer_id)
        except Exception as error:
            self._handle_error(error)
        else:
            self._check_response(cancel_response)
