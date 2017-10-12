import tensorflow as tf
from tensorforce import Configuration
from tensorforce.agents import VPGAgent
from tensorforce.core.networks.layers import conv2d, flatten, dense, nonlinearity, linear
from .market_env import MarketEnv

def get_agent(mode, window, dbs, train_steps, test_steps):
    if mode == 'testing':
        env = MarketEnv(dbs=dbs, steps=test_steps, window=window, testing=True)
    elif mode == 'training':
        env = MarketEnv(dbs=dbs, steps=train_steps, window=window)

    def network(window_length, env):
        def network_builder(inputs, summary_level=0):
            x = inputs['prices']
            last_w = inputs['last_action']

            regularization = 1e-8

            x = conv2d(x=x, size=2, window=(1, 3), bias=True, activation='relu', l2_regularization=regularization, padding='VALID',
                       scope='conv2d0')
            x = conv2d(x=x, size=20, window=(1, window_length - 2), bias=True, activation='relu', l2_regularization=regularization,
                       padding='VALID', scope='conv2d1')

            x = tf.concat([x, last_w], axis=3)

            x = conv2d(x=x, size=1, window=(1, 1), bias=True, activation='relu', l2_regularization=regularization, padding='VALID',
                       scope='conv2d2')
            x = flatten(x, scope='flatten0')
            x = dense(x, size=7, activation='relu', bias=True, l2_regularization=regularization, scope='dense0')

            x = tf.nn.softmax(x)

            return x

        return network_builder


    agent = VPGAgent(
        Configuration(
            log_level='debug',
            batch_size=50,
            discount=1,

            optimizer='adam',
            optimizer_batch_size=50,

            tf_summary='/output/logs',
            tf_sumary_interval=100,
            gae_reward=True,
            gae_lambda=0.97,
            sample_actions=False,

            learning_rate=3e-5,
            epochs=30,
            normalize_advantage=True,
            # exploration=dict(type='epsilondecay',
            #                  epsilon=1,
            #                  epsilon_final=0.05,
            #                  epsilon_timesteps=100*10**3,
            #                  start_after=0),
            states=env.states,
            actions=env.actions,
            network=network(window, env)
        ))

    return agent, env