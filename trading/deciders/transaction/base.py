from abc import ABC, abstractclassmethod


class Decider(ABC):
    @abstractclassmethod
    def decide(self):
        pass

    @abstractclassmethod
    def apply_last(self):
        pass
