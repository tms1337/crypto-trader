from trading.deciders.volume.base import VolumeDecider


class FixedValueVolumeDecider(VolumeDecider):
    def __init__(self, value):
        self.value = value

    def decide(self, partial_decisions):
        for decision in partial_decisions:
            decision.volume = self.value

        return partial_decisions

