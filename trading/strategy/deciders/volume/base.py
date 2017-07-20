from abc import ABC, abstractclassmethod

from trading.strategy.deciders.decider import Decider


class VolumeDecider(Decider, ABC):
    @abstractclassmethod
    def decide(self, partial_decisions):
        pass
