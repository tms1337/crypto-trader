from trading.deciders.volume.base import VolumeDecider


class FixedValueVolumeDecider(VolumeDecider):
    def __init__(self, value):
        self.value = value

    def decide(self, partial_decision):
        return self.value

