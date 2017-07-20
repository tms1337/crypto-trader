from abc import ABC, abstractclassmethod

from trading.strategy.deciders.decider import Decider


class OfferDecider(ABC):
    @abstractclassmethod
    def decide(self, stats_matrix):
        pass

    @abstractclassmethod
    def apply_last(self):
        pass
