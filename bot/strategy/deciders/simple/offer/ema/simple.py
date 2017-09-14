import copy

import math

from bot.strategy.deciders.simple.offer.ema.ema import EmaDecider
from util.logging import LoggableMixin

import numpy as np


class SimpleEmaOfferDecider(EmaDecider, LoggableMixin):
    def __init__(self,
                 currencies,
                 trading_currency,
                 buy_threshold=0.01,
                 sell_threshold=0.01,
                 first_period=12,
                 second_period=26):

        self.was = False
        self.percent = 0.05

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
            history = self.history[exchange][currency]

            return (history[-2].volume < history[-1].volume) and \
                   (history[-2].close - history[-2].open > 0) and \
                   (history[-1].close - history[-1].open > 0) and \
                   (history[-1].high > history[-2].high and history[-1].low > history[-2].low)

            max_price = max([(i, history[i].last) for i in range(len(history) - 1)], key=lambda x: x[1])
            price = history[-1].last

            if self.was and price < self.last_applied_decision_record.get(exchange, currency).price:
                return False

            return self.ema_short[exchange][currency] < 0.98 * self.ema_long[exchange][currency]

            if len(self.ema_short_history[exchange][currency]) < 2:
                return False

            drop = (max_price[1] - price) / price
            drop /= len(history) - max_price[0]

            print('Drop', drop)

            return drop > 0.005
        else:
            return False

    def should_sell(self, exchange, currency, low, high):
        self._update_emas()

        if self._emas_ready():
            current_price = self.history[exchange][currency][-1].close
            last_price = self.last_applied_decision_record.get(exchange, currency).price

            margin = (current_price - last_price) / last_price

            # print('Margin', margin, self.percent)

            # if margin > self.percent:
            #     self.was = True
            #     self.percent *= (1 - self.percent)
            # elif margin < -self.percent:
            #     self.was = False
            #     self.percent *= (1 + self.percent)

            return margin > self.percent or margin < -self.percent
        else:
            return False
