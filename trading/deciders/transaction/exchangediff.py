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
        self.current_currency_index = 0

        self.verbose = verbose

        TransactionDecider.__init__(self, wrapper_container)

    def decide(self):
        decisions = []

        currency = self.currencies[self.current_currency_index]
        self.current_currency_index = (self.current_currency_index + 1) % \
                                      len(self.currencies)

        high_low_per_exchange = {}
        for exchange in self.wrapper_container.wrappers:
            wrapper = self.wrapper_container.wrappers[exchange]
            wrapper.stats_provider.set_currencies(currency,
                                                  self.trading_currency)

            high = wrapper.stats_provider.ticker_high()
            low = wrapper.stats_provider.ticker_low()

            high_low_per_exchange[exchange] = {"low": low, "high": high}

        max_margin = float("-Inf")
        best_exchanges = {}
        for first in high_low_per_exchange:
            for second in high_low_per_exchange:
                if first != second:
                    margin = high_low_per_exchange[first]["low"] - high_low_per_exchange[second]["high"]
                    if margin > max_margin:
                        max_margin = margin
                        best_exchanges["buy"] = second
                        best_exchanges["sell"] = first

                    margin = high_low_per_exchange[second]["low"] - high_low_per_exchange[first]["high"]
                    if margin > max_margin:
                        max_margin = margin
                        best_exchanges["buy"] = first
                        best_exchanges["sell"] = second

        if max_margin < 0:
            if self.verbose >= 1:
                print("No suitable difference to chose :(")
            return []
        else:
            low_decision = Decision()
            low_decision.base_currency = currency
            low_decision.quote_currency = self.trading_currency
            low_decision.transaction_type = TransactionType.SELL
            low_decision.exchange = best_exchanges["sell"]
            low_decision.price = high_low_per_exchange[best_exchanges["sell"]]["low"]

            high_decision = Decision()
            high_decision.base_currency = currency
            high_decision.quote_currency = self.trading_currency
            high_decision.transaction_type = TransactionType.BUY
            high_decision.exchange = best_exchanges["buy"]
            high_decision.price = high_low_per_exchange[best_exchanges["buy"]]["high"]

            decisions.append((low_decision, high_decision))

            return decisions

    def apply_last(self):
        pass
