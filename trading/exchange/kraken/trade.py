import krakenex

from .base import PrivateKrakenProvider
from ..base import CurrencyMixin, TradeProvider


class KrakenTradeProvider(PrivateKrakenProvider,
                          TradeProvider):
    def __init__(self,
                 key_uri,
                 base_currency=None,
                 quote_currency=None,
                 api=krakenex.API()):

        PrivateKrakenProvider.__init__(self,
                                       key_uri=key_uri,
                                       base_currency=base_currency,
                                       quote_currency=quote_currency,
                                       api=api)

    def total_balance(self, currency=None):
        balance_response = self.k.query_private("Balance")
        self._check_response(balance_response)

        balance = balance_response["result"]

        if not currency is None:
            return float(balance[self.map_currency_balance(currency)])
        else:
            return {self.inverse_map_currency(k):float(balance[k]) for k in balance if k in ["XETH", "XXBT", "XICN", "XXLM"]}

    def inverse_map_currency(self, currency):
        inverse_currency_map = {
            "XXBT": "BTC",
            "XETH": "ETH",
            "XICN": "ICN",
            "XXLM": "XLM"
        }

        if currency in inverse_currency_map:
            return inverse_currency_map[currency]
        else:
            return currency[1:]

    def create_buy_offer(self, volume, price=None):
        if price is None:
            return self._create_market_buy_offer(volume)
        else:
            offer_response = self.k.query_private("AddOrder", {"pair": "XETHXXBT",
                                                               "type": "buy",
                                                               "ordertype": "limit",
                                                               "price": "{0:.10f}".format(price),
                                                               "volume": "{0:.10f}".format(volume),
                                                               "trading_agreement": "agree"})
            self._check_response(offer_response)

            # TODO: check if multiple :(
            return offer_response["result"]["txid"][0]

    def create_sell_offer(self, volume, price=None):
        if price is None:
            return self._create_market_sell_offer(volume)
        else:
            offer_response = self.k.query_private("AddOrder", {"pair": self.form_pair(),
                                                               "type": "sell",
                                                               "ordertype": "limit",
                                                               "price": "{0:.10f}".format(price),
                                                               "volume": "{0:.10f}".format(volume),
                                                               "trading_agreement": "agree"})

            self._check_response(offer_response)

            return offer_response["result"]["txid"][0]

    def cancel_offer(self, offer_id):
        cancel_response = self.k.query_private("CancelOrder", {"txid": offer_id})

        self._check_response(cancel_response)

    def _create_market_buy_offer(self, volume):
        offer_response = self.k.query_private("AddOrder", {"pair": self.form_pair(),
                                                           "type": "buy",
                                                           "ordertype": "market",
                                                           "volume": "{0:.10f}".format(volume),
                                                           "trading_agreement": "agree"})
        self._check_response(offer_response)

        return offer_response["result"]["txid"][0]

    def _create_market_sell_offer(self, volume):
        offer_response = self.k.query_private("AddOrder", {"pair": self.form_pair(),
                                                           "type": "sell",
                                                           "ordertype": "market",
                                                           "volume": "{0:.10f}".format(volume),
                                                           "trading_agreement": "agree"})
        self._check_response(offer_response)

        return offer_response["result"]["txid"][0]

    def prepare_currencies(self, base_currency, quote_currency):
        self.set_currencies(base_currency, quote_currency)




