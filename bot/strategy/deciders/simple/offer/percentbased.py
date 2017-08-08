import copy

from bot.strategy.pipeline.data.infomatrix import InfoMatrix
from util.asserting import TypeChecker

from bot.strategy.deciders.simple.offer.base import OfferDecider
from bot.strategy.decision import Decision, OfferType
from bot.strategy.pipeline.data.statsmatrix import StatsMatrix
from bot.strategy.transaction import Transaction
from util.logging import LoggableMixin


class DecisionCell:
    offer_type = None
    price = None


class DecisionMatrix(InfoMatrix):
    def __init__(self, exchanges, currencies):
        InfoMatrix.__init__(self, exchanges, currencies, DecisionCell)


class PercentBasedOfferDecider(OfferDecider, LoggableMixin):
    def __init__(self,
                 currencies,
                 trading_currency,
                 buy_threshold,
                 sell_threshold,
                 security_loss_threshold):
        self.currencies = currencies
        self.trading_currency = trading_currency

        TypeChecker.check_type(buy_threshold, float)
        assert 0 <= buy_threshold < 1, \
            "Buy threshold must be in [0, 1) interval, value of %f given" % buy_threshold
        self.buy_threshold = buy_threshold

        TypeChecker.check_one_of_types(sell_threshold, [float, int])
        assert sell_threshold > 0, \
            "Sell threshold must be greater than 0, value of %f given" % buy_threshold
        self.sell_threshold = sell_threshold

        TypeChecker.check_type(security_loss_threshold, float)
        assert security_loss_threshold > 0, \
            "Security loss threshold must be greater than 0, value of %f given" % security_loss_threshold
        assert security_loss_threshold > buy_threshold, \
            "Security loss threshold must be greater than buy threshold, value of %f <= %f given" \
            % (security_loss_threshold, buy_threshold)
        self.security_loss_threshold = security_loss_threshold

        self.last_decision_record = None
        self.last_applied_decision_record = None

        LoggableMixin.__init__(self, PercentBasedOfferDecider)

    def decide(self, informer):
        super(PercentBasedOfferDecider, self).decide(informer)

        stats_matrix = informer.get_stats_matrix()
        TypeChecker.check_type(stats_matrix, StatsMatrix)

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

                    self.logger.debug("Exchange %s, currency %s", (exchange, currency))

                    low = stats_matrix.get(exchange, currency).low
                    high = stats_matrix.get(exchange, currency).high
                    last = stats_matrix.get(exchange, currency).last
                    last_applied_price = self.last_applied_decision_record.get(exchange, currency).price
                    last_applied_decision = self.last_applied_decision_record.get(exchange, currency).offer_type

                    buy_margin = (last_applied_price - high) / last_applied_price
                    sell_margin = (low - last_applied_price) / last_applied_price

                    self.logger.debug("\tBuy margin %f / %f" % (buy_margin, self.buy_threshold))
                    self.logger.debug("\tSell margin %f / %f" % (sell_margin, self.sell_threshold))

                    if (last_applied_decision == OfferType.BUY and sell_margin >= self.sell_threshold) or \
                            (last_applied_decision == OfferType.BUY and sell_margin <= -self.security_loss_threshold):

                        decision = Decision()
                        decision.exchange = exchange
                        decision.base_currency = currency
                        decision.quote_currency = self.trading_currency
                        decision.transaction_type = OfferType.SELL
                        decision.price = low
                        decision.decider = self

                        self.logger.debug("Made %s decision %s with sell margin %f" % (currency, decision, sell_margin))
                        transaction.add_decision(decision)

                        cell = DecisionCell()
                        cell.price = low
                        cell.offer_type = OfferType.SELL
                        self.last_decision_record.set(exchange, currency, cell)
                    elif (last_applied_decision == OfferType.SELL or last_applied_decision is None) and \
                                    buy_margin >= self.buy_threshold:
                        decision = Decision()
                        decision.exchange = exchange
                        decision.base_currency = currency
                        decision.quote_currency = self.trading_currency
                        decision.transaction_type = OfferType.BUY
                        decision.price = high
                        decision.decider = self

                        self.logger.debug("Made %s decision %s with buy margin % f" % (currency, decision, buy_margin))
                        transaction.add_decision(decision)

                        cell = DecisionCell()
                        cell.price = high
                        cell.offer_type = OfferType.BUY
                        self.last_decision_record.set(exchange, currency, cell)
                    else:
                        cell = None
                        self.last_decision_record.set(exchange, currency, cell)

        return [transaction]

    def apply_last(self):
        self.logger.debug("Applying last transaction list")

        for e in self.last_applied_decision_record.all_exchanges():
            for c in self.last_applied_decision_record.all_currencies():
                cell = self.last_decision_record.get(e, c)
                if not cell is None:
                    self.last_applied_decision_record.set(e, c, cell)
