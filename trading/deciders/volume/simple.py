from trading.deciders.volume.base import VolumeDecider


class FixedValueVolumeDecider(VolumeDecider):
    def __init__(self, value, wrapper_container):
        self.value = value
        VolumeDecider.__init__(self, wrapper_container)

    def decide(self, partial_decisions):
        for decision in partial_decisions:
            decision.volume = self.value

        return partial_decisions

