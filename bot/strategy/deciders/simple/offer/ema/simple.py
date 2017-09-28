import copy

import math
import random

import time

from bot.strategy.deciders.simple.offer.ema.ema import EmaDecider
from bot.strategy.deciders.simple.offer.pairedtrades import DecisionCell, DecisionMatrix
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

        self.Q = np.zeros(100)
        self.Q_sell = np.zeros(100, 100)

        self.avg1 = None
        self.avg2 = None

        self.alpha = 0.1

        EmaDecider.__init__(self,
                            currencies,
                            trading_currency,
                            buy_threshold,
                            sell_threshold,
                            first_period,
                            second_period)
        LoggableMixin.__init__(self, SimpleEmaOfferDecider)

    def should_sell(self, exchange, currency, low, high):
        self._update_emas(exchange, currency)

        history = self.history[exchange][currency]
        if len(history) >= 2:
            curr = history[-1].close
            position = self.last_applied_decision_record.get(exchange, currency).price
            margin = (curr - position) / position

            if margin < -thresh:
                self._reward(self.avg1 / self.avg2, -2)

                return True

            return False
        else:
            return False

    def should_buy(self, exchange, currency, low, high):
        self._update_emas(exchange, currency)

        history = self.history[exchange][currency]
        if len(history) >= 2 and self.avg1 is not None:
            ratio = self.avg1 / self.avg2
            self.decision_s = ratio

            ind = int((ratio - 0.5) / 0.01)

            return  random.random() < math.exp(self.Q[ind])
        else:
            return False

    def _update_emas(self, exchange, currency):
        history = self.history[exchange][currency]
        curr = history[-1].close

        if random.random() < 0.001:
            if self.avg1 is None:
                self.avg1 = curr
            else:
                self.avg1 = 0.4 * self.avg1 + 0.6 * curr

            if self.avg2 is None:
                self.avg2 = curr
            else:
                self.avg2 = 0.01 * self.avg1 + 0.99 * curr

    def _reward(self, ratio, r):
        ind = int((self.decision_s - 0.5) / 0.01)
        ind_2 = int((ratio - 0.5) / 0.01)

        gamma = 0.7

        self.Q[ind] += self.alpha * (r + gamma*self.Q[ind_2] - self.Q[ind])


        print('Rewarding', self.alpha)
        print(self.Q)
        print(self.Q_sell)

