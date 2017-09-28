from bot.strategy.deciders.decider import Decider
from util.asserting import TypeChecker


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

    def decide(self, informer):
        data = {}
        all_transactions = []
        for d in self.deciders:
            transactions, decider_data = d.decide(informer)
            assert not transactions is None, \
                "Decided transaction list should not be None"
            TypeChecker.check_type(decider_data, dict)
            all_transactions.extend(transactions)
            data.update(decider_data)

        return all_transactions, data
