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

        self.was = False
        self.percent = 1
        self.first_time = True

        self.last_high = None
        self.last_low = None

        self.conseq = 1
        self.last_s = None
        self.last_sigma = None
        self.Q = np.random.rand(1000, 100)

        self.avg1 = None
        self.avg2 = None


        self.last_delta = None
        self.last_checkpoint = DecisionMatrix(['poloniex'],
                                              ['BTC'])

        self.volume_ind = 0
        self.volume_ind_long = 0
        self.alpha = 0.8

        EmaDecider.__init__(self,
                            currencies,
                            trading_currency,
                            buy_threshold,
                            sell_threshold,
                            first_period,
                            second_period)
        LoggableMixin.__init__(self, SimpleEmaOfferDecider)

    def should_sell(self, exchange, currency, low, high):
        self._update_emas()

        history = self.history[exchange][currency]
        if len(history) >= 2:
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

            return self.avg1 is not None and self.avg2 < 0.995 * self.avg1

            position = self.last_applied_decision_record .get(exchange, currency).price

            margin = (curr - position) / position

            volume = history[-1].volume
            gamma = 0.8
            if history[-1].type == 'BUY':
                self.volume_ind *= gamma
                self.volume_ind += volume * (1 - gamma)
            else:
                self.volume_ind *= gamma
                self.volume_ind -= volume  * (1 - gamma)

            thresh = 0.02
            if margin > thresh:
                return True

                self.conseq *= 1.2
                if self.conseq > 2:
                    self.conseq = 2

                cell = DecisionCell()
                cell.offer_type = self.last_applied_decision_record.get(exchange, currency).offer_type
                cell.price = curr

                self.last_applied_decision_record.set(exchange, currency, cell)

                return False
            elif margin < -thresh:
                self.conseq *= 0.3

                return True

            return False

            if random.random() < 0.001:
                print('sell', self.volume_ind, '/', 0.5 * curr * math.e ** (-self.conseq))

            should = self.volume_ind < - 0.5 * curr * math.e ** (-self.conseq)
            return should

            gamma = 0.8
            if should and margin > 0.01:
                self.conseq *= gamma
                self.conseq += 1 * (1 - gamma)

                print('Market state %f' % self.conseq)
            elif should and margin <= 0.01:
                self.conseq *= gamma
                self.conseq -= 1 - gamma

                print('Market state %f' % self.conseq)

            return should
        else:
            return False

    def should_buy(self, exchange, currency, low, high):
        self._update_emas()

        history = self.history[exchange][currency]
        if len(history) >= 2:
            curr = history[-1].close

            if random.random() < 0.001:
                if self.avg1 is None:
                    self.avg1 = curr
                else:
                    self.avg1 = 0.4 * self.avg1 + 0.6 * curr

                if self.avg2 is None:
                    self.avg2 = curr
                else:
                    self.avg2 = 0.01 * self.avg2 + 0.99 * curr

            if random.random() < 0.001:
                print(self.avg1, self.avg2)

            return self.avg1 is not None and self.avg2 > 1.005 * self.avg1

            position = self.last_applied_decision_record.get(exchange, currency).price

            margin = (curr - position) / position

            if self.conseq < 0.1:
                self.conseq *= 1.00001

            thresh = 0.05
            if margin < -thresh:
                self.conseq *= 0.3

                print('Under')
                cell = DecisionCell()
                cell.offer_type = self.last_applied_decision_record.get(exchange, currency).offer_type
                cell.price = curr

                self.last_applied_decision_record.set(exchange, currency, cell)

                return False
            elif margin > thresh:
                self.conseq *= 1.2
                if self.conseq > 2:
                    self.conseq = 2

                return self.conseq >= 1

            return False

            gamma = 0.8
            if history[-1].type == 'BUY':
                self.volume_ind *= gamma
                self.volume_ind += volume * (1 - gamma)
            else:
                self.volume_ind *= gamma
                self.volume_ind -= volume * (1 - gamma)

            if random.random() < 0.001:
                print('Proba %f' % (math.e ** ( (0.5 * self.conseq) - 1 )))
                print(self.volume_ind, 100 * 1 / self.conseq)

            if random.random() < math.e ** ( (0.5 * self.conseq) - 1 ):
                return curr > self.last_applied_decision_record.get(exchange, currency).price# self.volume_ind > 100 * 1 / self.conseq
            else:
                return False

            if random.random() < 0.001:
                print(self.volume_ind, '/', curr * math.e ** (-self.conseq))

            return self.volume_ind > curr * math.e ** (-self.conseq)

            rnd = random.random()

            if random.random() < 0.001:
                print(self.volume_ind)

            if rnd < 2 ** (0.5 * (self.conseq + 1)) - 0.9:
                return self.volume_ind >= 50
            else:
                return False

            should = self.volume_ind >= 10
            if should:
                pass
                # self.volume_ind = 0

            return should

            if self.first_time:
                cell = DecisionCell()
                cell.price = curr

                self.last_checkpoint.set(exchange, currency, cell)

                self.first_time = False
                return True

            position = self.last_checkpoint.get(exchange, currency).price

            margin = (curr - position) / position
            thresh = 0.03

            if margin > thresh:
                self.last_delta = 1

                cell = DecisionCell()
                cell.price = curr

                self.last_checkpoint.set(exchange, currency, cell)
            elif margin <= -thresh:
                self.last_delta = -1

                cell = DecisionCell()
                cell.price = curr

                self.last_checkpoint.set(exchange, currency, cell)

            return (self.last_delta == 1)
        else:
            return False
