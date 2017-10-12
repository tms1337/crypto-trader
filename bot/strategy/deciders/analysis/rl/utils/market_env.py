import random

import numpy as np
from tensorforce.core.distributions import Distribution
from tensorforce.environments.environment import Environment

import tensorflow as tf

class SoftmaxDistro(Distribution):
    def sample(self):
        return self.x

    def create_tf_operations(self, x, deterministic):
        self.x = x

    def log_probability(self, action):
        return tf.log(action)

    def __iter__(self):
        return super().__iter__()

    def entropy(self):
        pass

    @classmethod
    def from_tensors(cls, tensors, deterministic):
        pass

    def get_tensors(self):
        pass

    @staticmethod
    def from_config(config, kwargs=None):
        return super().from_config(config, kwargs)

    def kl_divergence(self, other):
        pass


class MarketEnv(Environment):
    def __init__(self, dbs, steps, window=50, testing=False, steps_per_cursor=100, episode_len=50):
        self.dbs = dbs
        self.crypto_n = len(dbs)
        self.steps = steps
        self.window = window
        self.testing = testing

        self.feature_n = 3
        self.data = self._generate_data()

        self.episode_len = episode_len

        self.cursor = window + 1
        self.in_cursor = 0
        self.steps_per_cursor = steps_per_cursor

        self.last_action = np.zeros((self.crypto_n + 1,))
        self.last_action[0] = 1

        self.all_rewards = []

    def reset(self):
        self.cursor += 1
        self.in_cursor = 0

        state = self._preprocess_state(self._current_state())

        last_action = self.last_action[1:].reshape((self.crypto_n, 1, 1))
        return {'prices': state, 'last_action': last_action}

    def execute(self, action):
        action = np.array(action)

        if random.random() < 0.001:
            print('Action before', action)

        action = np.exp(action)
        action /= np.sum(action)

        current_state = self._current_state()
        next_state = self._next_state()

        fee = 0.2 / 100
        fee_factor = 1 - fee * np.sum(np.abs(action[1:] - self.last_action[1:]))

        y = next_state[:, -1, 0] / current_state[:, -1, 0]

        if self.testing:
            reward = action[0] + fee_factor * np.dot(action[1:].T, y)
            self.all_rewards.append(reward)
        else:
            reward = np.log(action[0] + fee_factor * np.dot(action[1:].T, y))

        if random.random() < 0.001:
            print('Action after', action[1:])
            print('y', y)
            print('log(y)', np.log(y))
            print('fee factor', fee_factor)
            print('reward', reward)

        self.last_action = action

        last_action = self.last_action[1:].reshape((self.crypto_n, 1, 1))
        state = np.array(self._preprocess_state(self._current_state()))
        is_terminal = self.in_cursor == self.episode_len or \
                      (self.in_cursor + self.window + 1) == self.steps

        return {'prices': state, 'last_action': last_action}, \
               reward, \
               is_terminal

    def close(self):
        pass

    @property
    def rewards(self):
        return self.all_rewards

    @property
    def states(self):
        return dict(
            prices=dict(shape=(self.crypto_n, self.window, self.feature_n),
                        type='float'),
            last_action=dict(shape=(self.crypto_n, 1, 1), type='float')
        )

    @property
    def actions(self):
        return dict(continuous=True,
                    shape=(self.crypto_n + 1,),
                    distribution=SoftmaxDistro())

    @staticmethod
    def _preprocess_state(state, copy=False):
        if copy:
            state = np.copy(state)

        for i in range(state.shape[0]):
            state[i] /= state[i, -1, 0]

        return state

    def _current_state(self):
        position = self.cursor + self.in_cursor

        state = np.copy(self.data[:, position-self.window:position, :])

        return state

    def _next_state(self):
        self.in_cursor += 1

        return self._current_state()

    @staticmethod
    def _get_ohlcv(cursor):
        record = cursor.next()

        o = float(record['open'])
        h = float(record['high'])
        l = float(record['low'])
        c = float(record['close'])
        v = float(record['volume'])

        return o, h, l, c, v

    def _generate_data(self):
        data = np.ndarray((self.crypto_n, self.steps, self.feature_n), dtype=float)

        for i in range(self.steps):
            if i % (10 ** 3) == 0:
                print(i, '/', self.steps)

            for j, db in enumerate(self.dbs):
                o, h, l, c, v = self._get_ohlcv(db)
                data[j, i, 0] = c
                data[j, i, 1] = h
                data[j, i, 2] = l

        return data

    def __str__(self):
        return 'Market environment'