from trading.strategy.deciders.decider import Decider
from trading.strategy.deciders.simple.offer.base import OfferDecider
from trading.strategy.deciders.simple.volume.base import VolumeDecider
from trading.util.typechecker import TypeChecker


class SimpleCompositeDecider(Decider):
    def __init__(self,
                 trade_provider,
                 offer_decider,
                 volume_decider):

        TypeChecker.check_type(offer_decider, OfferDecider)
        TypeChecker.check_type(volume_decider, VolumeDecider)

        self.offer_decider = offer_decider
        self.volume_decider = volume_decider

        Decider.__init__(self, trade_provider)

    def decide(self, stats_matrix):
        transactions = self.offer_decider.decide(stats_matrix)
        transactions = self.volume_decider.decide(transactions)

