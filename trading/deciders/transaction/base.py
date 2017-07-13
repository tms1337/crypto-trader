from abc import ABC, abstractclassmethod

from trading.exchange.base import ExchangeWrapperContainer
from ..decider import Decider


class TransactionDecider(ABC, Decider):
    @abstractclassmethod
    def decide(self):
        pass

    @abstractclassmethod
    def apply_last(self):
        pass
