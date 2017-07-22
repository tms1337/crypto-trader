from trading.strategy.deciders.simple.volume.base import VolumeDecider
from trading.util.asserting import TypeChecker


class FixedValueVolumeDecider(VolumeDecider):
    def __init__(self, values):
        TypeChecker.check_type(values, dict)
        for k in values:
            TypeChecker.check_type(k, str)
            TypeChecker.check_type(values[k], float)

        self.values = values

    def decide(self, transactions, informer):
        for transaction in transactions:
            for decision in transaction.decisions:
                decision.volume = self.values[decision.base_currency]

        return transactions

    def apply_last(self):
        pass



