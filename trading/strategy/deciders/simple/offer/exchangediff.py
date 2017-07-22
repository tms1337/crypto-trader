from trading.exchange.base import CurrencyMixin
from trading.strategy.decision import Decision, OfferType
from trading.strategy.pipeline.data.statsmatrix import StatsMatrix
from trading.strategy.transaction import Transaction
from trading.util.asserting import TypeChecker
from trading.util.logging import LoggableMixin
from .base import OfferDecider


class ExchangeDiffOfferDecider(OfferDecider, LoggableMixin):
    def __init__(self,
                 currencies,
                 trading_currency):

        self.trading_currency = trading_currency
        CurrencyMixin.check_currency(trading_currency)

        for curr in currencies:
            CurrencyMixin.check_currency(curr)
        self.currencies = currencies
        self.current_currency_index = 0

        LoggableMixin.__init__(self, ExchangeDiffOfferDecider)
        OfferDecider.__init__(self)

    def decide(self, informer):
        super(ExchangeDiffOfferDecider, self).decide(informer)

        stats_matrix = informer.get_stats_matrix()
        TypeChecker.check_type(stats_matrix, StatsMatrix)

        transaction = Transaction()

        assert 0 <= self.current_currency_index < len(self.currencies)

        currency = self.currencies[self.current_currency_index]
        self.current_currency_index = (self.current_currency_index + 1) % \
                                      len(self.currencies)

        assert 0 <= self.current_currency_index < len(self.currencies)

        max_margin = float("-Inf")
        best_exchanges = {}
        for first in stats_matrix.all_exchanges():
            for second in stats_matrix.all_exchanges():
                if first != second:
                    self.logger.debug("Checking exchange pair (%s, %s)" % (first, second))

                    margin = stats_matrix.get(first, currency).low - stats_matrix.get(second, currency).high
                    self.logger.debug("\tMargin in order %f", margin)

                    if margin > max_margin:
                        max_margin = margin
                        best_exchanges["buy"] = second
                        best_exchanges["sell"] = first
                        self.logger.debug("Found new max margin %f" % max_margin)

        if max_margin < 0:
            self.logger.debug("No suitable difference to chose, going to backup method")

            max_margin = float("-Inf")
            best_exchanges = {}
            for first in stats_matrix.all_exchanges():
                for second in stats_matrix.all_exchanges():
                    if first != second:
                        self.logger.debug("Checking exchange pair (%s, %s)" % (first, second))

                        margin = stats_matrix.get(first, currency).last - stats_matrix.get(second, currency).last
                        self.logger.debug("\tMargin in order %f", margin)

                        if margin > max_margin:
                            max_margin = margin
                            best_exchanges["buy"] = second
                            best_exchanges["sell"] = first
                            self.logger.debug("Found new max margin %f" % max_margin)

        if max_margin > 0:
            low_decision = Decision()
            low_decision.base_currency = currency
            low_decision.quote_currency = self.trading_currency
            low_decision.transaction_type = OfferType.SELL
            low_decision.exchange = best_exchanges["sell"]
            low_decision.price = stats_matrix.get(best_exchanges["sell"], currency).low
            low_decision.decider = self

            self.logger.debug("Low decision chosen %s" % low_decision)

            high_decision = Decision()
            high_decision.base_currency = currency
            high_decision.quote_currency = self.trading_currency
            high_decision.transaction_type = OfferType.BUY
            high_decision.exchange = best_exchanges["buy"]
            high_decision.price = stats_matrix.get(best_exchanges["buy"], currency).high
            high_decision.decider = self

            self.logger.debug("High decision chosen %s " % high_decision)

            transaction.add_decision(low_decision)
            transaction.add_decision(high_decision)

        return [transaction]

    def apply_last(self):
        pass