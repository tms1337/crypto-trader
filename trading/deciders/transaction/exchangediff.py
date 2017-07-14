from trading.deciders.decision import Decision, TransactionType
from trading.exchange.base import CurrencyMixin
from .base import TransactionDecider
import math


class ExchangeDiffDecider(TransactionDecider):
    def __init__(self,
                 currencies,
                 base_currency,
                 wrapper_container,
                 verbose=0):

        self.trading_currency = base_currency
        CurrencyMixin.check_currency(base_currency)

        for curr in currencies:
            CurrencyMixin.check_currency(curr)
        self.currencies = currencies

        self.verbose = verbose

        TransactionDecider.__init__(self, wrapper_container)

    def decide(self):
        decisions = []

        for currency in self.currencies:
            low, high = (None, float("inf")), (None, float("-inf"))
            for exchange in self.wrapper_container.wrappers:
                wrapper = self.wrapper_container.wrappers[exchange]
                wrapper.stats_provider.set_currencies(currency,
                                                      self.trading_currency)
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

            low_decision = Decision()
            low_decision.base_currency = currency
            low_decision.quote_currency = self.trading_currency
            low_decision.transaction_type = TransactionType.BUY
            low_decision.exchange = low[0]
            low_decision.price = low[1]

            high_decision = Decision()
            high_decision.base_currency = currency
            high_decision.quote_currency = self.trading_currency
            high_decision.transaction_type = TransactionType.SELL
            high_decision.exchange = high[0]
            high_decision.price = high[1]

            decisions.append( (low_decision, high_decision) )

        return decisions


    def apply_last(self):
        pass
