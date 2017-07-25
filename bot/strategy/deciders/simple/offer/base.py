from abc import ABC, abstractclassmethod

from bot.strategy.deciders.decider import Decider
from bot.strategy.pipeline.informer import Informer
from bot.util.asserting import TypeChecker


class OfferDecider(ABC):
    @abstractclassmethod
    def decide(self, informer):
        TypeChecker.check_type(informer, Informer)

    @abstractclassmethod
    def apply_last(self):
        pass
