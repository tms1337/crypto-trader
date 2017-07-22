from abc import ABC, abstractclassmethod

from trading.strategy.deciders.decider import Decider
from trading.strategy.pipeline.informer import Informer
from trading.util.asserting import TypeChecker


class OfferDecider(ABC):
    @abstractclassmethod
    def decide(self, informer):
        TypeChecker.check_type(informer, Informer)

    @abstractclassmethod
    def apply_last(self):
        pass
