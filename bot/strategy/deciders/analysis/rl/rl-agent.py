import random

import sys
from collections import Counter

from keras import layers
from tensorforce.core.networks import layers as tensorforce_layers
from pymongo import MongoClient
from tensorforce import Configuration
from tensorforce import TensorForceError
from tensorforce import util
from tensorforce.agents import PPOAgent
from tensorforce.agents import VPGAgent
from tensorforce.core.networks import layered_network_builder
from tensorforce.core.networks.layers import conv2d, flatten, dense, nonlinearity
from tensorforce.environments.environment import Environment
import numpy as np
from tensorforce.execution import Runner

import tensorflow as tf

mode = sys.argv[1]


class MarketEnv(Environment):
    def __init__(self, dbs, steps, window=50, testing=False):
        self.dbs = dbs
        self.crypto_n = len(dbs)
        self.steps = steps
        self.window = window
        self.testing = testing

        self.feature_n = 3
        self.data = self._generate_data()

        self.cursor = 0

        self.last_action = np.zeros((self.crypto_n + 1,))
        # self.last_action[0, 0] = 1

    def reset(self):
        if not self.testing:
            self.cursor = random.randint(0, self.data.shape[1] - self.window - 2)
        else:
            self.cursor = 0

        initial_state = self._preprocess_state(self._next_state())

        return {'prices': initial_state, 'last_action': self.last_action}

    def execute(self, action):
        action = sorted(action.items(), key=lambda x: x[0])
        action = np.array([k[1] for k in action])

        action = np.exp(action)
        action /= np.sum(action)

        current_state = self._current_state()
        next_state = self._next_state()

        y = next_state[:, -1, 0] / current_state[:, -1, 0]

        reward = np.log(np.dot(action[1:].T, y))

        if random.random() < 0.001:
            print('Action after', action[1:])
            print('y', y)
            print('log(y)', np.log(y))
            print('reward', reward)

        if self.last_action is None:
            self.last_action = action

        last_action = self.last_action
        state = np.array(self._preprocess_state(self._current_state()))
        is_terminal = self.cursor + self.window + 1 == self.data.shape[1]

        self.last_action = action

        return {'prices': state, 'last_action': last_action}, \
               reward, \
               is_terminal

    def close(self):
        pass

    @property
    def states(self):
        return dict(
            prices=dict(shape=(self.crypto_n, self.window, self.feature_n),
                 type='float'),
            last_action=dict(shape=(self.crypto_n + 1,), type='float')
        )

    @property
    def actions(self):
        return {str(i): dict(continuous=True, min_value=-10, max_value=10)
                for i in range(self.crypto_n + 1)}

    @staticmethod
    def _preprocess_state(state, copy=False):
        if copy:
            state = np.copy(state)

        for i in range(state.shape[0]):
            state[i] /= state[i, -1, 0]

        return state

    def _current_state(self):
        state = np.copy(self.data[:, self.cursor:self.cursor + self.window, :])

        return state

    def _next_state(self):
        self.cursor += 1

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


mongo_host = 'ec2-52-56-38-131.eu-west-2.compute.amazonaws.com'
mongo_port = 27017

client = MongoClient(mongo_host, mongo_port)
db = client['historicalData']

period = '30min'

btc_db = db['poloniex_btc_usdt_%s' % period].find()
eth_db = db['poloniex_eth_usdt_%s' % period].find()
# etc_db = db['poloniex_etc_usdt_30min'].find()
dash_db = db['poloniex_dash_usdt_%s' % period].find()
ltc_db = db['poloniex_ltc_usdt_%s' % period].find()
xmr_db = db['poloniex_xmr_usdt_%s' % period].find()
xrp_db = db['poloniex_xrp_usdt_%s' % period].find()

dbs = [btc_db, eth_db, xrp_db, dash_db, ltc_db, xmr_db]
train_steps = 20 * 10 ** 3

for db in dbs:
    db.batch_size(train_steps)

if mode == 'testing':
    for db in dbs:
        db.skip(train_steps)

window = 50
test_steps = 15000

if mode == 'testing':
    env = MarketEnv(dbs=dbs, steps=test_steps, window=window, testing=True)
elif mode == 'training':
    env = MarketEnv(dbs=dbs, steps=train_steps, window=window)


def network(layers_config):
    def network_builder(inputs, summary_level=0):
        print(inputs)

        x = inputs['prices']
        last_w = inputs['last_action']

        internal_inputs = []
        internal_outputs = []
        internal_inits = []

        layer_counter = Counter()
        for layer_config in layers_config:
            if callable(layer_config['type']):
                scope = layer_config['type'].__name__ + str(layer_counter[layer_config['type']])
            else:
                scope = layer_config['type'] + str(layer_counter[layer_config['type']])

            x = util.get_object(
                obj=layer_config,
                predefined=tensorforce_layers,
                kwargs=dict(x=x, scope=scope, summary_level=summary_level)
            )
            layer_counter[layer_config['type']] += 1
            if isinstance(x, list) or isinstance(x, tuple):
                assert len(x) == 4
                internal_inputs.extend(x[1])
                internal_outputs.extend(x[2])
                internal_inits.extend(x[3])
                x = x[0]

        if internal_inputs:
            return x, internal_inputs, internal_outputs, internal_inits
        else:
            return x

    return network_builder


agent = VPGAgent(
    Configuration(
        log_level='debug',
        batch_size=50,
        optimizer='adam',
        discount=0,
        # tf_summary='/output/logs',
        gae_reward=True,
        gae_lambda=0.97,
        sample_actions=True,

        learning_rate=3e-5,
        epochs=10,
        optimizer_batch_size=100,
        normalize_advantage=False,
        exploration=dict(type='epsilondecay',
                         epsilon=0,
                         epsilon_final=0.1,
                         epsilon_timesteps=1e4,
                         start_after=0),
        states=env.states,
        actions=env.actions,
        network=network([
            dict(type='conv2d', size=2, window=(1, 3)),
            dict(type='conv2d', size=20, window=(1, window - 2)),
            dict(type='conv2d', size=1, window=(1, 1)),
            dict(type='flatten')
        ])
    ))

if mode == 'testing':
    agent.load_model('/models/agent.model-1449189')

runner = Runner(agent=agent, environment=env)


def episode_finished(r):
    print("Finished episode {ep} after {ts} timesteps (reward: {reward})".format(ep=r.episode,
                                                                                 ts=r.timestep,
                                                                                 reward=r.episode_rewards[-1]))
    return True


if mode == 'training':
    runner.run(episodes=500, max_timesteps=5000, episode_finished=episode_finished)

    agent.save_model('/output/agent.model')
elif mode == 'testing':
    runner.run(episodes=1, max_timesteps=test_steps, episode_finished=episode_finished)
