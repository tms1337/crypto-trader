from trading.exchange.base import CurrencyMixin
from .base import TransactionDecider
import math


class ExchangeDiffDecider(TransactionDecider):
    def __init__(self,
                 currencies,
                 base_currency,
                 wrapper_container,
                 verbose=0):

        self.base_currency = base_currency
        CurrencyMixin.check_currency(base_currency)

        for curr in currencies:
            CurrencyMixin.check_currency(curr)
        self.currencies = currencies

        self.verbose = verbose

        TransactionDecider.__init__(self, wrapper_container)

    def decide(self):
        for currency in self.currencies:
            low, high = (None, float("inf")), (None, float("-inf"))
            for exchange in self.wrapper_container.wrappers:
                wrapper = self.wrapper_container.wrappers[exchange]
                wrapper.stats_provider.set_currencies(self.base_currency,
                                                      currency)
                price = wrapper.stats_provider.ticker_price()

                if price > high[1]:
                    if self.verbose >= 2:
                        print("Setting high price for %s at (%s, %f)" % (currency, exchange, price))
                    high = (exchange, price)

                if price < low[1]:
                    if self.verbose >= 2:
                        print("Setting low price for %s at (%s, %f)" % (currency, exchange, price))
                    low = (exchange, price)

            if self.verbose >= 1:
                print("Chose low high for %s at %s and %s" % (currency, low, high))

    def apply_last(self):
        pass
