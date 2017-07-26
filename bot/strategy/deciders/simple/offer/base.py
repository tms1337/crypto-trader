from abc import ABC, abstractclassmethod

from bot.strategy.pipeline.informer import Informer
from util.asserting import TypeChecker


class OfferDecider(ABC):
    @abstractclassmethod
    def decide(self, informer):
        TypeChecker.check_type(informer, Informer)

    @abstractclassmethod
    def apply_last(self):
        pass
