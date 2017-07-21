from trading.strategy.deciders.decider import Decider
from trading.util.asserting import TypeChecker


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
        all_transactions = []
        for d in self.deciders:
            transactions = d.decide(stats_matrix)
            assert not transactions is None, \
                "Decided transaction list should not be None"
            all_transactions.extend(transactions)

        return all_transactions
