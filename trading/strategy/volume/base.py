from abc import ABC, abstractclassmethod
from ..decider import Decider


class VolumeDecider(Decider, ABC):
    @abstractclassmethod
    def decide(self, partial_decisions):
        pass
