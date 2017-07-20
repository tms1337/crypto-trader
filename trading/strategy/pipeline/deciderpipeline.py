from trading.strategy.deciders.decider import Decider
from trading.util.typechecker import TypeChecker


class DeciderPipeline:
    def __init__(self, deciders=None):
        if deciders is None:
            deciders = []

        TypeChecker.check_type(deciders, list)
        for d in deciders:
            TypeChecker.check_type(d, Decider)

        self.deciders = deciders

    def add_decider(self, decider):
        TypeChecker.check_type(decider, Decider)
        self.deciders.append(decider)

    def decide(self, stats_matrix):
        pass
