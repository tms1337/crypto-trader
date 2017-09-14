from abc import ABC

from bot.strategy.deciders.simple.offer.base import OfferDecider
from bot.strategy.deciders.simple.offer.pairedtrades import PairedTradesOfferDecider
from util.asserting import TypeChecker
from util.logging import LoggableMixin


class HistoryOfferDecider(PairedTradesOfferDecider, LoggableMixin):
    def __init__(self,
                 currencies,
                 trading_currency,
                 period):
        TypeChecker.check_type(period, int)
        assert period > 0, "First period must be greater than 0"
        self.period = period

        self.history = {}
        self.first_price = {}

        PairedTradesOfferDecider.__init__(self, currencies, trading_currency)
        LoggableMixin.__init__(self, HistoryOfferDecider)

    def update_stats(self, stats_matrix):
        for e in stats_matrix.all_exchanges():
            if e not in self.history:
                self.history[e] = {}

            if e not in self.first_price:
                self.first_price[e] = {}

            for c in stats_matrix.all_currencies():
                last = stats_matrix.get(e, c).last
                if last is None:
                    continue

                if c not in self.history[e]:
                    self.history[e][c] = []

                self.history[e][c].append(stats_matrix.get(e, c))
                self.history[e][c] = self.history[e][c][-self.period-1:]

                if c not in self.first_price[e]:
                    self.first_price[e][c] = last
