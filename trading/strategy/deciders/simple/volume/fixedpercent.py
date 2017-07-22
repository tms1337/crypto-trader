from trading.strategy.deciders.simple.volume.base import VolumeDecider
from trading.util.asserting import TypeChecker
from trading.util.logging import LoggableMixin


class FixedPercentVolumeDecider(VolumeDecider, LoggableMixin):
    def __init__(self, percent):
        TypeChecker.check_one_of_types(percent, [float, int])
        assert 0 <= percent <= 1, "Percent should be in range [0, 1]"

        self.percent = percent

        LoggableMixin.__init__(self, FixedPercentVolumeDecider)

    def decide(self, transactions, informer):
        pass

    def apply_last(self):
        pass
