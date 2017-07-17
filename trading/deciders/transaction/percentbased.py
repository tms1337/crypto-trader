import logging
import time

from trading.deciders.decision import Decision, TransactionType
from trading.deciders.transaction.base import TransactionDecider
from trading.exchange.base import CurrencyMixin
import copy


class PercentBasedTransactionDecider(TransactionDecider):
    def __init__(self,
                 currencies,
                 trading_currency,
                 buy_threshold,
                 sell_threshold,
                 wrapper_container,
                 logger_name="app"):

        self.trading_currency = trading_currency
        CurrencyMixin.check_currency(trading_currency)

        for curr in currencies:
            CurrencyMixin.check_currency(curr)
        self.currencies = currencies

        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.wrapper_container = wrapper_container

        self.last_transaction_types = {exchange: {currency: None for currency in currencies}
                                       for exchange in wrapper_container.wrappers}

        self.last_prices = {exchange: {currency: None for currency in currencies}
                            for exchange in wrapper_container.wrappers}

        self.last_applied_prices = copy.deepcopy(self.last_prices)

        self.logger_name = logger_name
        self.logger = logging.getLogger("%s.PercentBased" % logger_name)

        TransactionDecider.__init__(self, wrapper_container)

    def decide(self, prev_decisions):
        decisions = []

        for exchange in self.wrapper_container.wrappers:
            wrapper = self.wrapper_container.wrappers[exchange]
            stats = wrapper.stats_provider

            for currency in self.currencies:
                stats.set_currencies(currency,
                                     self.trading_currency)

                low = stats.ticker_high()
                time.sleep(1)
                high = stats.ticker_low()

                last_type = self.last_transaction_types[exchange][currency]
                last_price = self.last_applied_prices[exchange][currency]

                if last_type is None:
                    # first time :)
                    self.last_prices[exchange][currency] = high

                    decision = Decision()
                    decision.exchange = exchange
                    decision.base_currency = currency
                    decision.quote_currency = self.trading_currency
                    decision.transaction_type = TransactionType.BUY
                    decision.price = high

                    decisions.append(decision)

                    self.last_transaction_types[exchange][currency] = TransactionType.BUY
                else:
                    sell_margin = (low - last_price) / last_price
                    buy_margin = (last_price - high) / last_price

                    if last_type == TransactionType.BUY and sell_margin > self.sell_threshold:

                        decision = Decision()
                        decision.exchange = exchange
                        decision.base_currency = currency
                        decision.quote_currency = self.trading_currency
                        decision.transaction_type = TransactionType.SELL
                        decision.price = low

                        decisions.append(decision)

                        self.last_transaction_types[exchange][currency] = TransactionType.SELL
                    elif last_type == TransactionType.SELL and buy_margin > self.buy_threshold:
                        decision = Decision()
                        decision.exchange = exchange
                        decision.base_currency = currency
                        decision.quote_currency = self.trading_currency
                        decision.transaction_type = TransactionType.BUY
                        decision.price = high

                        decisions.append(decision)

                        self.last_transaction_types[exchange][currency] = TransactionType.BUY

        return decisions

    def apply_last(self):
        self.last_applied_prices = copy.deepcopy(self.last_prices)
