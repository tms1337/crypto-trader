from abc import ABC, abstractclassmethod

from trading.strategy.deciders.decider import Decider


class VolumeDecider(ABC):
    @abstractclassmethod
    def decide(self, transactions, informer):
        pass

    @abstractclassmethod
    def apply_last(self):
        pass

