from keras.optimizers import Adam

from bot.strategy.deciders.simple.offer.ema.ema import EmaDecider
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.losses import mean_squared_error as mse

import numpy as np

class ReinforcementEmaOfferDecider(EmaDecider):
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

        self.buy_nn = Sequential()
        self.buy_nn.add(Dense(10, input_shape=(3,), activation='relu'))
        self.buy_nn.add(Dropout(0.25))
        self.buy_nn.add(Dense(1, activation='softmax'))

        self.buy_nn.compile(optimizer=Adam(lr=0.0001),
                            loss=mse,
                            metrics=[mse])

        self.sell_nn = Sequential()
        self.sell_nn.add(Dense(10, input_shape=(3,), activation='relu'))
        self.sell_nn.add(Dropout(0.25))
        self.sell_nn.add(Dense(1, activation='softmax'))

        self.sell_nn.compile(optimizer=Adam(lr=0.0001),
                             loss=mse,
                             metrics=[mse])

    @staticmethod
    def _softmax(x):
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum(axis=0)

    @staticmethod
    def _calc_Q(nn, state):
        return nn.predict_on_batch([state])[0]

    def should_buy(self, exchange, currency, low, high):
        self._update_emas()

        if self._emas_ready():
            short_ema = self.ema_short[exchange][currency]
            long_ema = self.ema_long[exchange][currency]

            Q = []
            for v in [0, 1]:
                action_value_pair = (v, self._calc_Q(self.buy_nn, (short_ema, long_ema, v)))
                Q.append(action_value_pair)

            softmax_values = self._softmax([q[1] for q in Q])

            chosen_index = np.random.choice(len(Q), 1, p=softmax_values)[0]

            chosen_action = Q[chosen_index][0]

            self.last_state_action = (short_ema, long_ema, chosen_action)
            self.last_nn = self.buy_nn

            return chosen_action == 1
        else:
            return False

    def should_sell(self, exchange, currency, low, high):
        self._update_emas()

        if self._emas_ready():
            return self.ema_short[exchange][currency] > 1.02 * self.ema_long[exchange][currency]
        else:
            return False

    def apply_reward(self, reward):
        x = np.array([self.last_state_action])

        Q = self._calc_Q(self.last_nn, self.last_state_action)
        # y = Q + self.alpha * (reward + self.gamma * )

        # self.last_nn.fit()
