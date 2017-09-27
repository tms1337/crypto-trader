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

    def _update_emas(self):
        for e in self.history:

            if e not in self.ema_short_history:
                self.ema_short_history[e] = { c: [] for c in self.history[e] }

            if e not in self.ema_long_history:
                self.ema_long_history[e] = { c: [] for c in self.history[e] }

            for c in self.history[e]:
                if len(self.history[e][c]) < self.period:
                    return

                if e not in self.ema_short:
                    self.ema_short[e] = {}

                if e not in self.ema_long:
                    self.ema_long[e] = {}

                # self.ema_short[e][c] = self.alpha_short * sum([(1 - self.alpha_short) ** (i - 1) * self.history[e][c][-i].close
                #                               for i in range(1, self.short_period)])
                # self.ema_short_history[e][c].append(self.ema_short[e][c])


                # self.ema_long[e][c] = self.alpha_long * sum([(1 - self.alpha_long) ** (i - 1) * self.history[e][c][-i].close
                #                                          for i in range(1, self.long_period)])
                # self.ema_long_history[e][c].append(self.ema_long[e][c])


    def _emas_ready(self):
        return True
        return self.ema_short != {} and self.ema_long != {}