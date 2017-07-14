from trading.deciders.volume.base import VolumeDecider


class FixedValueVolumeDecider(VolumeDecider):
    def __init__(self, value, wrapper_container):
        self.value = value
        VolumeDecider.__init__(self, wrapper_container)

    def decide(self, partial_decisions):
        for decision in partial_decisions:
            if isinstance(decision, tuple):
                for d in decision:
                    d.volume = self.value
            else:
                decision.volume = self.value

        return partial_decisions

