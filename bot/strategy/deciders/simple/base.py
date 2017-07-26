from bot.strategy.deciders.decider import Decider
from bot.strategy.deciders.simple.offer.base import OfferDecider
from bot.strategy.deciders.simple.volume.base import VolumeDecider
from util.asserting import TypeChecker


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

    def decide(self, informer):
        Decider.decide(self, informer)

        transactions = self.offer_decider.decide(informer)
        transactions = self.volume_decider.decide(transactions, informer)

        return transactions

    def apply_last(self):
        assert not self.offer_decider is None, "offer_decider should not be None"
        assert not self.volume_decider is None, "volume_decider should not be None"

        self.offer_decider.apply_last()
        self.volume_decider.apply_last()


