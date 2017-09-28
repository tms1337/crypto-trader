from bot.strategy.deciders.simple.offer.indicatorbased import IndicatorPairedTradesOfferDecider
from util.asserting import TypeChecker


class EmaOfferDecider(IndicatorPairedTradesOfferDecider):
    def __init__(self,
                 currencies,
                 trading_currency,
                 ema_factors):
        TypeChecker.check_type(ema_factors, list)
        for ema_period in ema_factors:
            TypeChecker.check_one_of_types(ema_period, [float, int])
            assert 0 < ema_period < 1

        self.ema_factors = ema_factors
        self.emas = {}

        IndicatorPairedTradesOfferDecider.__init__(self,
                                                   currencies,
                                                   trading_currency)

    def _update_indicators(self, informer):
        stats_matrix = informer.get_stats_matrix()

        for ema_factor in self.ema_factors:
            if ema_factor not in self.emas:
                pass
            else:
                pass
