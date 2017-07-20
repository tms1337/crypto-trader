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
                 security_loss_threshold,
                 wrapper_container,
                 logger_name="app",
                 every_n=5):

        self.trading_currency = trading_currency
        CurrencyMixin.check_currency(trading_currency)

        self.every_n = every_n
        self.i = 0

        for curr in currencies:
            CurrencyMixin.check_currency(curr)
        self.currencies = currencies

        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.security_loss_threshold = security_loss_threshold

        self.wrapper_container = wrapper_container

        self.last_transaction_types = {exchange: {currency: None for currency in currencies}
                                               for exchange in wrapper_container.wrappers}

        self.last_prices = {exchange: {currency: None for currency in currencies}
                            for exchange in wrapper_container.wrappers}

        self.last_applied_prices = copy.deepcopy(self.last_prices)
        self.last_applied_transaction_types = copy.deepcopy(self.last_transaction_types)

        self.logger_name = logger_name
        self.logger = logging.getLogger("%s.PercentBased" % logger_name)

        TransactionDecider.__init__(self, wrapper_container)

    def decide(self, prev_decisions):
        self.logger.debug("Last transaction types %s" % self.last_applied_transaction_types)

        # if self.i % self.every_n == 0:
        for exchange in self.wrapper_container.wrappers:
            self.logger.debug("Checking exchange: %s" % exchange)
            wrapper = self.wrapper_container.wrappers[exchange]
            stats = wrapper.stats_provider

            for currency in self.currencies:
                self.logger.debug("\tChecking currency %s" % currency)

                stats.set_currencies(currency,
                                     self.trading_currency)

                last = stats.ticker_last()
                low = last
                high = last

                last_type = self.last_applied_transaction_types[exchange][currency]
                last_price = self.last_applied_prices[exchange][currency]

                if last_type is None:
                    # first time :)
                    decision = Decision()
                    decision.exchange = exchange
                    decision.base_currency = currency
                    decision.quote_currency = self.trading_currency
                    decision.transaction_type = TransactionType.BUY
                    decision.price = high
                    decision.decider = self

                    prev_decisions.append(decision)

                    self.last_transaction_types[exchange][currency] = TransactionType.BUY
                    self.last_prices[exchange][currency] = high
                else:
                    sell_margin = (low - last_price) / last_price
                    buy_margin = (last_price - high) / last_price

                    if (last_type == TransactionType.BUY and sell_margin >= self.sell_threshold) or \
                        (last_type == TransactionType.BUY and sell_margin < -self.security_loss_threshold):

                        decision = Decision()
                        decision.exchange = exchange
                        decision.base_currency = currency
                        decision.quote_currency = self.trading_currency
                        decision.transaction_type = TransactionType.SELL
                        decision.price = low
                        decision.decider = self

                        prev_decisions.append(decision)

                        self.last_transaction_types[exchange][currency] = TransactionType.SELL
                        self.last_prices[exchange][currency] = decision.price
                    elif last_type == TransactionType.SELL and buy_margin >= self.buy_threshold:
                        decision = Decision()
                        decision.exchange = exchange
                        decision.base_currency = currency
                        decision.quote_currency = self.trading_currency
                        decision.transaction_type = TransactionType.BUY
                        decision.price = high
                        decision.decider = self

                        prev_decisions.append(decision)

                        self.last_transaction_types[exchange][currency] = TransactionType.BUY
                        self.last_prices[exchange][currency] = decision.price

        return prev_decisions
        # else:
        #     self.i = (self.i + 1) % self.every_n

    def apply_last(self):
        self.last_applied_prices = copy.deepcopy(self.last_prices)
        self.last_applied_transaction_types = copy.deepcopy(self.last_transaction_types)
