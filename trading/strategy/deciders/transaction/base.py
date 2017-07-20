from abc import ABC, abstractclassmethod

from trading.strategy.deciders.decider import Decider


class TransactionDecider(ABC, Decider):
    @abstractclassmethod
    def decide(self, prev_decisions):
        pass

    @abstractclassmethod
    def apply_last(self):
        pass
