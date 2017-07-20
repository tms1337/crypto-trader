from .client import bittrex

from .base import PrivateBittrexProvider
from ..base import CurrencyMixin, TradeProvider


class BittrexTradeProvider(PrivateBittrexProvider,
                           TradeProvider):
    def __init__(self,
                 key_uri,
                 base_currency=None,
                 quote_currency=None,
                 api=bittrex.bittrex(None, None)):
        PrivateBittrexProvider.__init__(self,
                                        key_uri=key_uri,
                                        base_currency=base_currency,
                                        quote_currency=quote_currency,
                                        api=api)

    def total_balance(self, currency=None):
        balance_response = self.api.getbalances()
        self._check_response(balance_response)

        if not currency is None:
            currency_balance = [b for b in balance_response if b["Currency"] == self.currency_mapping_for_balance(currency)]

            if len(currency_balance) == 0:
                return 0.0

            currency_balance = currency_balance[0]

            return float(currency_balance["Balance"])
        else:
            return {b["Currency"]: float(b["Balance"]) for b in balance_response}

    def create_buy_offer(self, volume, price=None):
        offer_response = self.api.buylimit(self.form_pair(),
                                           volume,
                                           price)
        self._check_response(offer_response)

        return offer_response["uuid"]

    def create_sell_offer(self, volume, price=None):
        offer_response = self.api.selllimit(self.form_pair(),
                                            volume,
                                            price)
        self._check_response(offer_response)

        return offer_response["uuid"]

    def cancel_offer(self, offer_id):
        cancel_response = self.api.cancel(offer_id)
        self._check_response(cancel_response)

    def prepare_currencies(self, base_currency, quote_currency):
        self.set_currencies(base_currency, quote_currency)
