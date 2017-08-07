from bot.strategy.deciders.simple.offer.base import OfferDecider
from bot.strategy.pipeline.informer import Informer
from util.asserting import TypeChecker
from util.logging import LoggableMixin


class EmaDecider(OfferDecider, LoggableMixin):
    def __init__(self,
                 first_period=20,
                 second_period=50):
        TypeChecker.check_type(first_period, int)
        assert first_period > 0, "First period must be greater than 0"
        self.first_period = first_period

        TypeChecker.check_type(second_period, int)
        assert second_period > 0, "Second period must be greater than 0"
        self.first_period = second_period

        self.first_history = [None for _ in range(first_period)]
        self.second_history = [None for _ in range(second_period)]

        LoggableMixin.__init__(self, EmaDecider)

    def decide(self, informer):
        TypeChecker.check_type(informer, Informer)
        stats_matrix = informer.stats_matrix

    def apply_last(self):
        pass
