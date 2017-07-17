import logging

from trading.deciders.decision import Decision, TransactionType
from trading.exchange.base import CurrencyMixin
from .base import TransactionDecider
import math


class ExchangeDiffDecider(TransactionDecider):
    def __init__(self,
                 currencies,
                 trading_currency,
                 wrapper_container,
                 logger_name="app"):

        self.trading_currency = trading_currency
        CurrencyMixin.check_currency(trading_currency)

        for curr in currencies:
            CurrencyMixin.check_currency(curr)
        self.currencies = currencies
        self.current_currency_index = 0

        self.logger_name = logger_name
        self.logger = logging.getLogger("%s.ExchangeDiffDecider" % logger_name)

        TransactionDecider.__init__(self, wrapper_container)

    def decide(self, prev_decisions):
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
                    self.logger.debug("Checking exchange pair (%s, %s)" % (first, second))
                    margin = high_low_per_exchange[first]["low"] - high_low_per_exchange[second]["high"]

                    if margin > max_margin:
                        max_margin = margin
                        best_exchanges["buy"] = second
                        best_exchanges["sell"] = first
                        self.logger.debug("Found new max margin %f" % max_margin)

                    margin = high_low_per_exchange[second]["low"] - high_low_per_exchange[first]["high"]
                    if margin > max_margin:
                        max_margin = margin
                        best_exchanges["buy"] = first
                        best_exchanges["sell"] = second
                        self.logger.debug("Found new max margin %f" % max_margin)

        if max_margin < 0:
            self.logger.debug("No suitable difference to chose :(")
            return []
        else:
            low_decision = Decision()
            low_decision.base_currency = currency
            low_decision.quote_currency = self.trading_currency
            low_decision.transaction_type = TransactionType.SELL
            low_decision.exchange = best_exchanges["sell"]
            low_decision.price = high_low_per_exchange[best_exchanges["sell"]]["low"]

            self.logger.debug("Low decision chosen %s" % low_decision)

            high_decision = Decision()
            high_decision.base_currency = currency
            high_decision.quote_currency = self.trading_currency
            high_decision.transaction_type = TransactionType.BUY
            high_decision.exchange = best_exchanges["buy"]
            high_decision.price = high_low_per_exchange[best_exchanges["buy"]]["high"]

            self.logger.debug("High decision chosen %s" % high_decision)

            decisions.append((high_decision, low_decision))

            return decisions

    def apply_last(self):
        pass


class ExchangeDiffBackup(TransactionDecider):
    def __init__(self,
                 currencies,
                 base_currency,
                 wrapper_container,
                 price_margin_perc=0.1,
                 logger_name="app"):

        self.trading_currency = base_currency
        CurrencyMixin.check_currency(base_currency)

        for curr in currencies:
            CurrencyMixin.check_currency(curr)
        self.currencies = currencies
        self.current_currency_index = 0

        self.price_margin_perc = price_margin_perc
        self.logger_name = logger_name
        self.logger = logging.getLogger("%s.DiffBackup" % self.logger_name)

        TransactionDecider.__init__(self, wrapper_container)

    def decide(self, prev_decisions):
        if not(prev_decisions is None or len(prev_decisions) == 0):
            return prev_decisions

        decisions = []

        currency = self.currencies[self.current_currency_index]
        self.current_currency_index = (self.current_currency_index + 1) % \
                                      len(self.currencies)

        low, high = (None, float("inf")), (None, float("-inf"))
        for exchange in self.wrapper_container.wrappers:
            wrapper = self.wrapper_container.wrappers[exchange]
            wrapper.stats_provider.set_currencies(currency,
                                                  self.trading_currency)
            price = wrapper.stats_provider.ticker_last()

            if price > high[1]:
                self.logger.debug("Setting high price for %s at (%s, %f)" % (currency, exchange, price))
                high = (exchange, price)

            if price < low[1]:
                self.logger.debug("Setting low price for %s at (%s, %f)" % (currency, exchange, price))
                low = (exchange, price)

        self.logger.info("Chose low high for %s at %s and %s" % (currency, low, high))

        # to ensure faster transaction
        self.price_margin_perc = 0.1
        price_margin = self.price_margin_perc * abs(high[1] - low[1])

        low_decision = Decision()
        low_decision.base_currency = currency
        low_decision.quote_currency = self.trading_currency
        low_decision.transaction_type = TransactionType.BUY
        low_decision.exchange = low[0]
        low_decision.price = low[1] + price_margin

        high_decision = Decision()
        high_decision.base_currency = currency
        high_decision.quote_currency = self.trading_currency
        high_decision.transaction_type = TransactionType.SELL
        high_decision.exchange = high[0]
        high_decision.price = high[1] - price_margin

        self.logger.info("Chose decision pair (%s, %s)" % (low_decision, high_decision))

        decisions.append((low_decision, high_decision))

        return decisions

    def apply_last(self):
        super().apply_last()
