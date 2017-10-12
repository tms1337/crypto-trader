import sys

from pymongo import MongoClient
from tensorforce.core.distributions import Distribution
from tensorforce.execution import Runner

mode = sys.argv[1]

from utils.agnt import get_agent
from utils.market_env import MarketEnv
from utils.mcdb import get_montecarlo_db

import tensorflow as tf

mode = sys.argv[1]
data_source = sys.argv[2]


if data_source == 'mc':
    mongo_host = 'ec2-52-56-38-131.eu-west-2.compute.amazonaws.com'
    mongo_port = 27017

    client = MongoClient(mongo_host, mongo_port)
    db = client['historicalData']

    period = '30min_all'

    btc_db = db['poloniex_btc_usdt_%s' % period].find()
    eth_db = db['poloniex_eth_usdt_%s' % period].find()
    dash_db = db['poloniex_dash_usdt_%s' % period].find()
    ltc_db = db['poloniex_ltc_usdt_%s' % period].find()
    xmr_db = db['poloniex_xmr_usdt_%s' % period].find()
    xrp_db = db['poloniex_xrp_usdt_%s' % period].find()

    btc_db = get_montecarlo_db(btc_db, 45000, init_price=1e4)
    eth_db = get_montecarlo_db(eth_db, 30000, init_price=1e4)
    dash_db = get_montecarlo_db(dash_db, 46000, init_price=1e4)
    xmr_db = get_montecarlo_db(xmr_db, 46000, init_price=1e4)
    xrp_db = get_montecarlo_db(xrp_db, 45900, init_price=1e4)
    ltc_db = get_montecarlo_db(ltc_db, 45000, init_price=1e4)
else:
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

if data_source == 'mc':
    train_steps = 40 * 10 ** 3
else:
    train_steps = 20 * 10**3

for db in dbs:
    db.batch_size(train_steps)

if mode == 'testing':
    for db in dbs:
        db.skip(train_steps)

window = 50
test_steps = 15000

agent, env = get_agent(mode, window, dbs, train_steps, test_steps)

if mode == 'testing':
    agent.load_model('/models/agent.model-1370695')

runner = Runner(agent=agent, environment=env, deterministic=True)

def episode_finished(r):
    print("Finished episode {ep} after {ts} timesteps (reward: {reward})".format(ep=r.episode,
                                                                                 ts=r.timestep,
                                                                                 reward=r.episode_rewards[-1]))

    if (r.episode + 1) % 10 == 0:
        agent.save_model('/output/agent.model')

    return True

if mode == 'training':
    runner.run(episodes=2e6, max_timesteps=50, episode_finished=episode_finished)

    agent.save_model('/output/agent.model')
elif mode == 'testing':
    runner.run(episodes=1, max_timesteps=train_steps-window, episode_finished=episode_finished)

    with open('/output/rewards', mode='w+') as f:
        print(env.rewards, file=f)
