from bot.strategy.deciders.simple.offer.ema.ema import EmaDecider


class SimpleEmaOfferDecider(EmaDecider):
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