from bot.strategy.deciders.simple.offer.pairedtrades import PairedTradesOfferDecider
from util.logging import LoggableMixin


class MinimizeLossOfferDecider(PairedTradesOfferDecider):
    def __init__(self):
        PairedTradesOfferDecider.__init__(self)
        LoggableMixin.__init__(self, MinimizeLossOfferDecider)

    def should_buy(self, exchange, currency, low, high):
        pass

    def should_sell(self, exchange, currency, low, high):
        pass