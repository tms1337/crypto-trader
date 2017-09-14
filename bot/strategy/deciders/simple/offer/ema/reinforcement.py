from keras.optimizers import Adam

from bot.strategy.deciders.simple.offer.ema.ema import EmaDecider
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.losses import mean_squared_error as mse
from keras.initializers import RandomUniform

import numpy as np

from util.logging import LoggableMixin


class ReinforcementEmaOfferDecider(EmaDecider, LoggableMixin):
    def __init__(self,
                 currencies,
                 trading_currency,
                 buy_threshold=0.01,
                 sell_threshold=0.01,
                 first_period=12,
                 second_period=26,
                 gamma=0.5,
                 alpha=0.5):

        EmaDecider.__init__(self,
                            currencies,
                            trading_currency,
                            buy_threshold,
                            sell_threshold,
                            first_period,
                            second_period)

        self.gamma = gamma
        self.alpha = alpha

        self.buy_nn = Sequential()
        self.buy_nn.add(Dense(5, input_shape=(3,),
                              activation='relu',
                              kernel_initializer=RandomUniform(0, 0.5),
                              bias_initializer='zeros'))
        self.buy_nn.add(Dropout(0.25))
        self.buy_nn.add(Dense(1, activation='linear'))

        self.buy_nn.compile(optimizer=Adam(lr=0.001),
                            loss=mse,
                            metrics=[mse])

        self.sell_nn = Sequential()
        self.sell_nn.add(Dense(5, input_shape=(3,), activation='relu',
                               kernel_initializer=RandomUniform(0, 0.5),
                               bias_initializer='zeros'))
        self.buy_nn.add(Dropout(0.25))
        self.sell_nn.add(Dense(1, activation='linear'))

        self.sell_nn.compile(optimizer=Adam(lr=0.001),
                             loss=mse,
                             metrics=[mse])

        LoggableMixin.__init__(self, ReinforcementEmaOfferDecider)

    @staticmethod
    def _softmax(x):
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum()

    @staticmethod
    def _calc_Q(nn, state):
        prediction = nn.predict_on_batch(np.array([state]))
        return prediction[0]

    def should_buy(self, exchange, currency, low, high):
        self._update_emas()

        if self._emas_ready():
            short_ema = self.ema_short[exchange][currency]
            long_ema = self.ema_long[exchange][currency]

            max_ema = max([short_ema, long_ema])
            short_ema /= max_ema
            long_ema /= max_ema

            Q = []
            for v in [0, 1]:
                action_value_pair = (v, self._calc_Q(self.buy_nn, (short_ema, long_ema, v)))
                Q.append(action_value_pair)

            softmax_values = self._softmax([q[1] for q in Q]).flatten()

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
            short_ema = self.ema_short[exchange][currency]
            long_ema = self.ema_long[exchange][currency]

            max_ema = max([short_ema, long_ema])
            short_ema /= max_ema
            long_ema /= max_ema

            Q = []
            for v in [0, 1]:
                action_value_pair = (v, self._calc_Q(self.sell_nn, (short_ema, long_ema, v)))
                Q.append(action_value_pair)

            softmax_values = self._softmax([q[1] for q in Q]).flatten()

            chosen_index = np.random.choice(len(Q), 1, p=softmax_values)[0]

            chosen_action = Q[chosen_index][0]

            self.last_state_action = (short_ema, long_ema, chosen_action)
            self.last_nn = self.sell_nn

            return chosen_action == 1
        else:
            return False

    def apply_reward(self, reward):
        if self._emas_ready():
            x = np.array([self.last_state_action])

            Q = self._calc_Q(self.last_nn, self.last_state_action)

            state_action = list(self.last_state_action)
            qs = []
            for v in [0, 1]:
                state_action[2] = v
                qs.append(self._calc_Q(self.last_nn, state_action))
            max_Q = max(qs)

            y = Q + self.alpha * (reward + self.gamma * max_Q - Q)

            print('Comparison ', Q, y)

            self.last_nn.fit(x, y, epochs=1, batch_size=1, verbose=0)
