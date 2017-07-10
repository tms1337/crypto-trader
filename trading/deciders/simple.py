from trading.deciders.base import Decider


class AlwaysBuyDecider(Decider):
    def decide(self):
        super().decide()

    def apply_last(self):
        super().apply_last()