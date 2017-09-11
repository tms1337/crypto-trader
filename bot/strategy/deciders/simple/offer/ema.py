from bot.strategy.deciders.simple.offer.pairedtrades import PairedTradesOfferDecider
from util.asserting import TypeChecker
from util.logging import LoggableMixin


class EmaDecider(PairedTradesOfferDecider, LoggableMixin):
    def __init__(self,
                 currencies,
                 trading_currency,
                 buy_threshold=0.01,
                 sell_threshold=0.01,
                 first_period=12,
                 second_period=26,
                 alpha=0.5):
        TypeChecker.check_type(first_period, int)
        assert first_period > 0, "First period must be greater than 0"
        self.first_period = first_period

        TypeChecker.check_type(second_period, int)
        assert second_period > 0, "Second period must be greater than 0"
        self.second_period = second_period

        assert first_period != second_period, "Periods must be different"

        TypeChecker.check_type(alpha, float)
        assert alpha > 0, "Alpha must be greater than 0"
        assert alpha < 1, "Alpha must be less than 1"
        self.alpha = alpha

        TypeChecker.check_type(buy_threshold, float)
        assert buy_threshold > 0, "Buy threshold must be greater than 0"
        assert buy_threshold < 1, "Buy threshold must be less than 1"
        self.buy_threshold = buy_threshold

        TypeChecker.check_type(sell_threshold, float)
        assert sell_threshold > 0, "Sell threshold must be greater than 0"
        assert sell_threshold < 1, "Sell threshold must be less than 1"
        self.sell_threshold = sell_threshold

        self.first_history = {}
        self.second_history = {}

        PairedTradesOfferDecider.__init__(self, currencies, trading_currency)
        LoggableMixin.__init__(self, EmaDecider)

    def update_stats(self, stats_matrix):
        for e in stats_matrix.all_exchanges():
            if e not in self.first_history:
                self.first_history[e] = {}

            if e not in self.second_history:
                self.second_history[e] = {}

            for c in stats_matrix.all_currencies():
                last = stats_matrix.get(e, c).last
                if last is None:
                    continue

                if c not in self.first_history[e]:
                    self.first_history[e][c] = []

                self.first_history[e][c].append(last)
                self.first_history[e][c] = self.first_history[e][c][-self.first_period:]

                if c not in self.second_history[e]:
                    self.second_history[e][c] = []

                self.second_history[e][c].append(last)
                self.second_history[e][c] = self.second_history[e][c][-self.second_period:]

    def should_buy(self, exchange, currency, low, high):
        if len(self.first_history[exchange][currency]) < self.first_period or \
                        len(self.second_history[exchange][currency]) < self.second_period:
            return False
        else:
            ema_first = self.alpha * sum([(1 - self.alpha) ** (i) * self.first_history[exchange][currency][-i]
                                          for i in range(self.first_period)])
            ema_second = self.alpha * sum([(1 - self.alpha) ** (i) * self.second_history[exchange][currency][-i]
                                           for i in range(self.second_period)])

            self.logger.debug('EMA-%d: %f, EMA-%d: %f' % (self.first_period, ema_first, self.second_period, ema_second))

            if self.first_period < self.second_period:
                short_ema, long_ema = ema_first, ema_second
            else:
                short_ema, long_ema = ema_second, ema_first

            return (long_ema - short_ema) / short_ema > self.buy_threshold

    def should_sell(self, exchange, currency, low, high):
        if len(self.first_history[exchange][currency]) < self.first_period or \
                        len(self.second_history[exchange][currency]) < self.second_period:
            return False
        else:
            ema_first = self.alpha * sum([(1 - self.alpha) ** (i) * self.first_history[exchange][currency][-i]
                                          for i in range(self.first_period)])
            ema_second = self.alpha * sum([(1 - self.alpha) ** (i) * self.second_history[exchange][currency][-i]
                                           for i in range(self.second_period)])

            self.logger.debug('EMA-%d: %f, EMA-%d: %f' % (self.first_period, ema_first, self.second_period, ema_second))

            if self.first_period < self.second_period:
                short_ema, long_ema = ema_first, ema_second
            else:
                short_ema, long_ema = ema_second, ema_first

            return (short_ema - long_ema) / long_ema > self.sell_threshold
