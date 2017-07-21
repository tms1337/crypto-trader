from trading.strategy.deciders.decider import Decider
from trading.strategy.deciders.simple.offer.base import OfferDecider
from trading.strategy.deciders.simple.volume.base import VolumeDecider
from trading.util.asserting import TypeChecker


class SimpleCompositeDecider(Decider):
    def __init__(self,
                 trade_providers,
                 offer_decider,
                 volume_decider):
        TypeChecker.check_type(offer_decider, OfferDecider)
        TypeChecker.check_type(volume_decider, VolumeDecider)

        self.offer_decider = offer_decider
        self.volume_decider = volume_decider

        Decider.__init__(self, trade_providers)

    def decide(self, stats_matrix):
        transactions = self.offer_decider.decide(stats_matrix)
        transactions = self.volume_decider.decide(transactions)

        return transactions

    def apply_last(self):
        self.offer_decider.apply_last()
        self.volume_decider.apply_last()


