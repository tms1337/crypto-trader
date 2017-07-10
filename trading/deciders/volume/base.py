from abc import ABC, abstractclassmethod


class VolumeDecider(ABC):
    @abstractclassmethod
    def decide(self, partial_decision):
        pass
