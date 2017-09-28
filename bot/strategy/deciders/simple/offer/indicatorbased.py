from abc import abstractclassmethod

from bot.strategy.deciders.simple.offer.pairedtrades import PairedTradesOfferDecider


class IndicatorPairedTradesOfferDecider(PairedTradesOfferDecider):
    @abstractclassmethod
    def _update_indicators(self, informer):
        pass

    def decide(self, informer):
        self._update_indicators(informer)
        PairedTradesOfferDecider.decide(self, informer)
