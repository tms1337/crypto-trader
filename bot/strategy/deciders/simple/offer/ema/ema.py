import random

from bot.strategy.deciders.simple.offer.historydecider import HistoryOfferDecider
from util.asserting import TypeChecker
from util.logging import LoggableMixin


class EmaDecider(HistoryOfferDecider, LoggableMixin):
    def __init__(self,
                 currencies,
                 trading_currency,
                 buy_threshold=0.01,
                 sell_threshold=0.01,
                 first_period=12,
                 second_period=26):
        TypeChecker.check_type(first_period, int)
        assert first_period > 0, "First period must be greater than 0"
        self.short_period = first_period

        TypeChecker.check_type(second_period, int)
        assert second_period > 0, "Second period must be greater than 0"
        self.long_period = second_period

        assert first_period != second_period, "Periods must be different"

        if self.short_period > self.long_period:
            self.short_period, self.long_period = self.long_period, self.short_period

        self.alpha_short = 2 / (self.short_period + 1)
        self.alpha_long = 2 / (self.long_period + 1)
        self.ema_short, self.ema_long = {}, {}
        self.ema_short_history, self.ema_long_history = {}, {}


        TypeChecker.check_type(buy_threshold, float)
        assert buy_threshold > 0, "Buy threshold must be greater than 0"
        assert buy_threshold < 1, "Buy threshold must be less than 1"
        self.buy_threshold = buy_threshold

        TypeChecker.check_type(sell_threshold, float)
        assert sell_threshold > 0, "Sell threshold must be greater than 0"
        assert sell_threshold < 1, "Sell threshold must be less than 1"
        self.sell_threshold = sell_threshold

        HistoryOfferDecider.__init__(self, currencies, trading_currency, self.long_period)
        LoggableMixin.__init__(self, EmaDecider)

    def _update_emas(self, exchange, currency):
        pass

    def _emas_ready(self):
        return True
        return self.ema_short != {} and self.ema_long != {}