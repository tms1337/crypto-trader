import copy

from trading.strategy.deciders.simple.volume.base import VolumeDecider
from trading.util.asserting import TypeChecker


class FixedValueVolumeDecider(VolumeDecider):
    def __init__(self, values, iceberg_n=5):
        TypeChecker.check_type(values, dict)
        for k in values:
            TypeChecker.check_type(k, str)
            TypeChecker.check_type(values[k], float)

        self.values = values

        TypeChecker.check_one_of_types(iceberg_n, [float, int])
        self.iceberg_n = iceberg_n

    def decide(self, transactions, informer):
        for transaction in transactions:
            for decision in transaction.decisions:
                decision.volume = self.values[decision.base_currency]

        return transactions

    def apply_last(self):
        pass



