import copy
from abc import ABC, abstractclassmethod

from bot.strategy.deciders.simple.offer.base import OfferDecider
from bot.strategy.decision import OfferType, Decision
from bot.strategy.pipeline.data.infomatrix import InfoMatrix
from bot.strategy.pipeline.data.statsmatrix import StatsMatrix
from bot.strategy.transaction import Transaction
from util.asserting import TypeChecker
from util.logging import LoggableMixin


class DecisionCell:
    offer_type = None
    price = None


class DecisionMatrix(InfoMatrix):
    def __init__(self, exchanges, currencies):
        InfoMatrix.__init__(self, exchanges, currencies, DecisionCell)


class PairedTradesOfferDecider(OfferDecider, LoggableMixin):
    def __init__(self, currencies, trading_currency):
        self.last_decision_record = None
        self.last_applied_decision_record = None

        self.currencies = currencies
        self.trading_currency = trading_currency

        LoggableMixin.__init__(self, PairedTradesOfferDecider)

    def decide(self, informer):
        super(PairedTradesOfferDecider, self).decide(informer)

        stats_matrix = informer.get_stats_matrix()
        TypeChecker.check_type(stats_matrix, StatsMatrix)
        self.update_stats(stats_matrix)

        self.logger.debug("Starting decision process")
        TypeChecker.check_type(stats_matrix, StatsMatrix)

        transaction = Transaction()

        if self.last_decision_record is None:
            # first time :)
            self.logger.debug("Initializing last prices and offer types")

            self.last_decision_record = DecisionMatrix(stats_matrix.all_exchanges(),
                                                       stats_matrix.all_currencies())

            for e in self.last_decision_record.all_exchanges():
                for c in self.last_decision_record.all_currencies():
                    cell = DecisionCell()
                    cell.offer_type = None
                    cell.price = stats_matrix.get(e, c).last

                    self.last_decision_record.set(e, c, cell)

            self.last_applied_decision_record = copy.deepcopy(self.last_decision_record)

        for exchange in stats_matrix.all_exchanges():
            skip_exchange = False
            for currency in stats_matrix.all_currencies():
                if stats_matrix.get(exchange, currency).low is None or \
                                stats_matrix.get(exchange, currency).high is None:
                    self.logger.warn("Skipping exchange %s bacause of missing info" % exchange)
                    skip_exchange = True

            if not skip_exchange:
                for currency in stats_matrix.all_currencies():
                    if currency == self.trading_currency:
                        continue

                    self.logger.debug("Exchange %s, currency %s" % (exchange, currency))

                    low = stats_matrix.get(exchange, currency).low
                    high = stats_matrix.get(exchange, currency).high
                    last = stats_matrix.get(exchange, currency).last

                    last_applied_decision = self.last_applied_decision_record.get(exchange, currency).offer_type

                    if (last_applied_decision == OfferType.BUY) and \
                            self.should_sell(exchange, currency, low, high):
                        decision = Decision()
                        decision.exchange = exchange
                        decision.base_currency = currency
                        decision.quote_currency = self.trading_currency
                        decision.transaction_type = OfferType.SELL
                        decision.price = last
                        decision.decider = self

                        transaction.add_decision(decision)

                        cell = DecisionCell()
                        cell.price = low
                        cell.offer_type = OfferType.SELL
                        self.last_decision_record.set(exchange, currency, cell)
                    elif (last_applied_decision == OfferType.SELL  or last_applied_decision is None) and \
                            self.should_buy(exchange, currency, low, high):
                        decision = Decision()
                        decision.exchange = exchange
                        decision.base_currency = currency
                        decision.quote_currency = self.trading_currency
                        decision.transaction_type = OfferType.BUY
                        decision.price = last
                        decision.decider = self

                        transaction.add_decision(decision)

                        cell = DecisionCell()
                        cell.price = high
                        cell.offer_type = OfferType.BUY
                        self.last_decision_record.set(exchange, currency, cell)
                    else:
                        cell = None
                        self.last_decision_record.set(exchange, currency, cell)

        return [transaction]

    def update_stats(self, stats_matrix):
        pass

    def should_buy(self, exchange, currency, low, high):
        pass

    def should_sell(self, exchange, currency, low, high):
        pass

    def apply_last(self):
        self.logger.debug("Applying last transaction list")

        for e in self.last_applied_decision_record.all_exchanges():
            for c in self.last_applied_decision_record.all_currencies():
                cell = self.last_decision_record.get(e, c)
                if not cell is None:
                    self.last_applied_decision_record.set(e, c, cell)
