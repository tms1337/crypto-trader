import copy
import logging

from trading.exchange.base import CurrencyMixin
from trading.strategy.deciders.simple.offer.base import OfferDecider
from trading.strategy.decision import Decision, OfferType
from trading.strategy.transaction import Transaction
from trading.util.logging import LoggableMixin


class PercentBasedOfferDecider(OfferDecider, LoggableMixin):
    def __init__(self,
                 currencies,
                 trading_currency,
                 buy_threshold,
                 sell_threshold,
                 security_loss_threshold):

        self.currencies = currencies
        self.trading_currency = trading_currency
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.security_loss_threshold = security_loss_threshold

        LoggableMixin.__init__(self)

    def decide(self, stats_matrix):
        transaction = Transaction()

        self.logger.debug("Last transaction types %s" % self.last_applied_transaction_types)

        for exchange in stats_matrix.all_exchanges():
            self.logger.debug("Checking exchange: %s" % exchange)
            for currency in stats_matrix.all_currencies():
                self.logger.debug("\tChecking currency %s" % currency)

                low = stats_matrix.get(exchange, currency).low
                high = stats_matrix.get(exchange, currency).high

                last_type = self.last_applied_transaction_types[exchange][currency]
                last_price = self.last_applied_prices[exchange][currency]

                if last_type is None:
                    # first time :)
                    decision = Decision()
                    decision.exchange = exchange
                    decision.base_currency = currency
                    decision.quote_currency = self.trading_currency
                    decision.transaction_type = OfferType.BUY
                    decision.price = high
                    decision.decider = self

                    transaction.add_decision(decision)

                    self.last_transaction_types[exchange][currency] = OfferType.BUY
                    self.last_prices[exchange][currency] = high
                else:
                    sell_margin = (low - last_price) / last_price
                    buy_margin = (last_price - high) / last_price

                    if (last_type == OfferType.BUY and sell_margin >= self.sell_threshold) or \
                            (last_type == OfferType.BUY and sell_margin < -self.security_loss_threshold):

                        decision = Decision()
                        decision.exchange = exchange
                        decision.base_currency = currency
                        decision.quote_currency = self.trading_currency
                        decision.transaction_type = OfferType.SELL
                        decision.price = low
                        decision.decider = self

                        transaction.add_decision(decision)

                        self.last_transaction_types[exchange][currency] = OfferType.SELL
                        self.last_prices[exchange][currency] = decision.price
                    elif last_type == OfferType.SELL and buy_margin >= self.buy_threshold:
                        decision = Decision()
                        decision.exchange = exchange
                        decision.base_currency = currency
                        decision.quote_currency = self.trading_currency
                        decision.transaction_type = OfferType.BUY
                        decision.price = high
                        decision.decider = self

                        transaction.add_decision(decision)

                        self.last_transaction_types[exchange][currency] = OfferType.BUY
                        self.last_prices[exchange][currency] = decision.price

        return transaction

    def apply_last(self):
        self.last_applied_prices = copy.deepcopy(self.last_prices)
        self.last_applied_transaction_types = copy.deepcopy(self.last_transaction_types)
