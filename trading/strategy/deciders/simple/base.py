from trading.strategy.deciders.offer.base import OfferDecider

from trading.strategy.deciders.simple.volume import VolumeDecider
from trading.util.typechecker import TypeChecker


class SimpleCompositeDecider:
    def __init__(self,
                 offer_decider,
                 volume_decider):

        TypeChecker.check_type(offer_decider, OfferDecider)
        TypeChecker.check_type(volume_decider, VolumeDecider)
