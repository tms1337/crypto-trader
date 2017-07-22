import copy
from trading.strategy.deciders.simple.offer.base import OfferDecider
from trading.strategy.decision import Decision, OfferType
from trading.strategy.pipeline.statsmatrix import StatsMatrix
from trading.strategy.transaction import Transaction
from trading.util.asserting import TypeChecker
from trading.util.logging import LoggableMixin


class OfferTypeMatrix:
    def __init__(self,
                 exchanges,
                 currencies):

        TypeChecker.check_type(exchanges, list)
        for e in exchanges:
            TypeChecker.check_type(e, str)

        TypeChecker.check_type(currencies, list)
        for c in currencies:
            TypeChecker.check_type(c, str)

        self.matrix = {e: {c: None for c in currencies} for e in exchanges}

    def get(self, exchange, currency):
        TypeChecker.check_type(exchange, str)
        TypeChecker.check_type(currency, str)

        assert exchange in self.matrix, "Exchange %s must be in matrix" % exchange
        assert currency in self.matrix[exchange], "Currency %s must be in matrix" % currency

    def set(self, exchange, currency, value):
        TypeChecker.check_type(exchange, str)
        TypeChecker.check_type(currency, str)
        TypeChecker.check_type(value, OfferType)

        assert exchange in self.matrix, "Exchange %s must be in matrix" % exchange
        assert currency in self.matrix[exchange], "Currency %s must be in matrix" % currency

        self.matrix[exchange][currency] = value


class DecisionRecord:
    def __init__(self,
                 stats_matrix,
                 offer_type_matrix):
        TypeChecker.check_type(stats_matrix, StatsMatrix)
        TypeChecker.check_type(offer_type_matrix, OfferTypeMatrix)

        self.stats_matrix = stats_matrix
        self.offer_type_matrix = offer_type_matrix


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

        self.last_decision_record = None
        self.last_applied_decision_record = None

        LoggableMixin.__init__(self, PercentBasedOfferDecider)

    def decide(self, informer):
        OfferDecider.decide(self, informer)

        stats_matrix = informer.get_stats_matrix()
        TypeChecker.check_type(stats_matrix, StatsMatrix)

        self.logger.debug("Starting decision process")
        TypeChecker.check_type(stats_matrix, StatsMatrix)

        transaction = Transaction()

        if self.last_decision_record is None:
            # first time :)
            self.logger.debug("Initializing last prices and offer types")
            offer_type_matrix = OfferTypeMatrix(stats_matrix.all_exchanges(),
                                                stats_matrix.all_currencies())
            self.last_decision_record = DecisionRecord(stats_matrix,
                                                       offer_type_matrix)

            self.last_applied_decision_record = copy.deepcopy(self.last_decision_record)
            for exchange in self.last_applied_decision_record.stats_matrix.all_exchanges():
                for currency in self.last_applied_decision_record.stats_matrix.all_currencies():
                    cell = self.last_applied_decision_record.stats_matrix.get(exchange, currency)
                    cell.price = cell.last

                    self.last_applied_decision_record.stats_matrix.set(exchange, currency, cell)

        else:
            self.last_decision_record.stats_matrix = stats_matrix

        for exchange in stats_matrix.all_exchanges():
            skip_exchange = False
            for currency in stats_matrix.all_currencies():
                if stats_matrix.get(exchange, currency).low is None or \
                        stats_matrix.get(exchange, currency).high is None:
                    self.logger.warn("Skipping exchange %s bacause of missing info" % exchange)
                    skip_exchange = True

            if not skip_exchange:
                for currency in stats_matrix.all_currencies():
                    low = stats_matrix.get(exchange, currency).low
                    high = stats_matrix.get(exchange, currency).high
                    last_applied_price = self.last_applied_decision_record.stats_matrix.get(exchange, currency).price
                    last_applied_decision = self.last_applied_decision_record.offer_type_matrix.get(exchange, currency)

                    buy_margin = (last_applied_price - high) / last_applied_price
                    sell_margin = (low - last_applied_price) / last_applied_price

                    if (last_applied_decision == OfferType.BUY and sell_margin >= self.sell_threshold) or \
                            (last_applied_decision == OfferType.BUY and sell_margin < -self.security_loss_threshold):

                        decision = Decision()
                        decision.exchange = exchange
                        decision.base_currency = currency
                        decision.quote_currency = self.trading_currency
                        decision.transaction_type = OfferType.SELL
                        decision.price = low
                        decision.decider = self

                        self.logger.debug("Made decision %s" % decision)
                        transaction.add_decision(decision)

                        self.last_decision_record.offer_type_matrix.set(exchange, currency, OfferType.SELL)
                    elif (last_applied_decision == OfferType.SELL or last_applied_decision is None) and \
                                    buy_margin >= self.buy_threshold:
                        decision = Decision()
                        decision.exchange = exchange
                        decision.base_currency = currency
                        decision.quote_currency = self.trading_currency
                        decision.transaction_type = OfferType.BUY
                        decision.price = high
                        decision.decider = self

                        self.logger.debug("Made decision %s" % decision)
                        transaction.add_decision(decision)

                        self.last_decision_record.offer_type_matrix.set(exchange, currency, OfferType.BUY)

        return [transaction]

    def apply_last(self):
        self.logger.debug("Applying last transaction list")
        self.last_applied_decision_record = copy.deepcopy(self.last_decision_record)
