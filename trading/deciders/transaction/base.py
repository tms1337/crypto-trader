from abc import ABC, abstractclassmethod


class TransactionDecider(ABC):
    @abstractclassmethod
    def decide(self):
        pass

    @abstractclassmethod
    def apply_last(self):
        pass

