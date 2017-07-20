from abc import ABC, abstractmethod


class Decider(ABC):
    @abstractmethod
    def decide(self, stats_matrix):
        pass

