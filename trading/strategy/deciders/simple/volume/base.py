from abc import ABC, abstractclassmethod

from trading.strategy.deciders.decider import Decider


class VolumeDecider(ABC):
    @abstractclassmethod
    def decide(self, transactions):
        pass
