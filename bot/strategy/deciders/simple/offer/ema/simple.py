from bot.strategy.deciders.simple.offer.ema.ema import EmaDecider
from util.logging import LoggableMixin


class SimpleEmaOfferDecider(EmaDecider, LoggableMixin):
    def __init__(self,
                 currencies,
                 trading_currency,
                 buy_threshold=0.01,
                 sell_threshold=0.01,
                 first_period=12,
                 second_period=26):

        EmaDecider.__init__(self,
                            currencies,
                            trading_currency,
                            buy_threshold,
                            sell_threshold,
                            first_period,
                            second_period)
        LoggableMixin.__init__(self, SimpleEmaOfferDecider)

    def should_buy(self, exchange, currency, low, high):
        self._update_emas()

        if self._emas_ready():
            return self.ema_short[exchange][currency] < 0.98 * self.ema_long[exchange][currency]
        else:
            return False

    def should_sell(self, exchange, currency, low, high):
        self._update_emas()

        if self._emas_ready():
            return self.ema_short[exchange][currency] > 1.02 * self.ema_long[exchange][currency]
        else:
            return False
