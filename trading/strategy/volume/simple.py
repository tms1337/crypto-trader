from trading.strategy.volume.base import VolumeDecider


class FixedValueVolumeDecider(VolumeDecider):
    def __init__(self, values, wrapper_container):
        self.values = values
        VolumeDecider.__init__(self, wrapper_container)

    def decide(self, partial_decisions):
        for decision in partial_decisions:
            if isinstance(decision, tuple):
                for d in decision:
                    if d.volume is None:
                        d.volume = self.values[d.base_currency]
            else:
                if decision.volume is None:
                    decision.volume = self.values[decision.base_currency]

        return partial_decisions

