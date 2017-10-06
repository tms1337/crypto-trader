import logging
import sys

from tensorforce import Configuration
from tensorforce.agents import Agent
from tensorforce.agents import VPGAgent
from tensorforce.core.networks import layered_network_builder

from bot.daemon import Daemon
from bot.exchange.bitfinex.trade import BitfinexTradeProvider
from bot.exchange.bittrex.stats import BittrexStatsProvider
from bot.exchange.bittrex.trade import BittrexTradeProvider
from bot.exchange.kraken.stats import KrakenStatsProvider
from bot.exchange.kraken.trade import KrakenTradeProvider
from bot.exchange.poloniex.stats import PoloniexStatsProvider
from bot.exchange.poloniex.trade import PoloniexTradeProvider
from bot.strategy.deciders.smart.rljianh17 import RLJianh17Decide
from bot.strategy.pipeline.block import Block
# from bot.strategy.deciders.smart.rljianh17 import RLJianh17Decide
from bot.strategy.pipeline.deciderpipeline import DeciderPipeline
from bot.strategy.pipeline.informer import Informer
from bot.strategy.pipeline.monitoring.mongobalancemonitor import MongoBalanceMonitor
from bot.strategy.pipeline.transactionexecutor import TransactionExecutor


logger = logging.getLogger('app')
logger.setLevel(logging.DEBUG)

# create file handler which logs even debug messages
fh = logging.FileHandler('debug.log')
fh.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)

# create formatter and add it to the handlers
formatter = logging.Formatter(fmt="[%(asctime)s / %(name)s / %(levelname)s / %(funcName)s]\t"
                                  "%(message)s", datefmt="%Y-%m-%d,%H:%M")
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

daemon_dt = float(sys.argv[2])
providers_pause_dt = 0.25

keys_path = sys.argv[1]

stats_providers = {
    "poloniex": PoloniexStatsProvider(pause_dt=providers_pause_dt),
    # "bittrex": BittrexStatsProvider(pause_dt=providers_pause_dt),
    # "bitfinex": BitfinexStatsProvider(),
    # "kraken": KrakenStatsProvider()
}
trade_providers = {
    "poloniex": PoloniexTradeProvider(key_uri=("%s/poloniex" % keys_path), pause_dt=providers_pause_dt),
    # "bittrex": BittrexTradeProvider(key_uri=("%s/bittrex" % keys_path), pause_dt=providers_pause_dt),
    # "bitfinex": BitfinexTradeProvider(key_uri=("%s/bitfinex" % keys_path)),
    # "kraken": KrakenTradeProvider(key_uri=("%s/kraken" % keys_path))
}

currencies_for_crypto = ["ETH", "LTC", "DASH", "XRP", "BTC", "XMR"]
trading_currency_for_crypto = "USD"

window = 50
agent_uri = sys.argv[3]
agent = VPGAgent(
    Configuration(
        log_level='debug',
        batch_size=50,
        optimizer='adam',
        discount=0,
        tf_summary='output/logs',
        gae_reward=True,
        gae_lambda=0.97,
        sample_actions=True,

        learning_rate=3e-5,
        epochs=20,
        optimizer_batch_size=100,
        normalize_advantage=False,
        exploration=dict(type='epsilondecay',
                         epsilon=0,
                         epsilon_final=0.1,
                         epsilon_timesteps=1e4,
                         start_after=0),
        states=dict(shape=(len(currencies_for_crypto), window, 3),
                    type='float'),
        actions={str(i): dict(continuous=True, min_value=-10, max_value=10)
                for i in range(len(currencies_for_crypto) + 1)},
        network=layered_network_builder([
            dict(type='conv2d', size=2, window=(1, 3)),
            dict(type='conv2d', size=20, window=(1, window - 2)),
            dict(type='conv2d', size=1, window=(1, 1)),
            dict(type='flatten')
        ])
    ))
print(agent_uri)
agent.load_model(agent_uri)

decider = RLJianh17Decide(agent=agent,
                          trade_providers=trade_providers)

crypto_informer = Informer(base_currency=trading_currency_for_crypto,
                           stats_providers=stats_providers,
                           trade_providers=trade_providers,
                           currencies=currencies_for_crypto,
                           historic_n=50,
                           interval=1800)


executor = TransactionExecutor(trade_providers=trade_providers)

crypto_block = Block(decider_pipeline=DeciderPipeline(deciders=[decider]),
                     informer=crypto_informer,
                     transaction_executor=executor,
                     monitors=[])

daemon = Daemon(blocks=[crypto_block],
                dt_seconds=daemon_dt)

if daemon is not None:
    daemon.run()


# i bot se mora malo odmoriti
"""
                                                   `..`
                                                   .++:`
                                                    /o+:
                                                .-- /o+/.
                                               `///:/+++-
                                               -/++++o++.
                                              `-///++++/`
                                           `.--::::::::-...``
                                        `.-::::://:::::------.``
                                       .::::///////////:::::----.
                                      .:://:::://+++///////::::::-`
                                     .///::::::::/+++/::::///:::::-`
                                    .///:::::::::-://:/ss/::/::::::-
                                   `////::::/++/:--//::ETH-://::::::-`
                                   :////::::DASH---:/::----://///::::-
                                  `///+/:::-+ys:--:///:::::///::::::::.
                                  -/////:--------:://////////::::::::::`
                                  //////::----:::////////////::::::---:/:-.`
                                 `/////////::://////////////////:::::::/+//::.`
                                 -////+++//////++++////////////////::::/oo++//:.
                             .--:///++++++++++++++++////////////////::::+so+++/:-
                          `-://++//+++++++++++++++++++++++///////////::::syo++///-
                        `-///++++/++++++++++++++++++++++++/////////////::+y:oo+++/-`
                      `-///++++://++++++++++++++++++++++++++++++///////::/s./++++//:.`
                    `-:://+++-``///++++++++++++o+++++++++++++o++////////::+`:o++/////::-..`
            .....---::::/++:`  .////+++++++++ooooo++++++++oydy++////////::  ++++////////::-
           .://///:://///+:    //++++++++++oooooooooooosydmmdo++++//////:- /o+++///////-.`
            `-///////////+.   `/+++++++++yyssssssyyyhddmmmmhs+++++/////:::.o++++///////:-`
          ``.-::://///////.  `./+++++++++oyddmmmmmmmmmmmdhso+++++//////:::-//////////////:-`
        `:::///////++++++//:::////+++++++++osyyhhhhhyysoo++++++++///////::---.---///:.--::-.
        `::::::////+++//////:::////+++++++++++++++++++++++++++++++/////:----:-...///:`   `
          ``  `:///:./////////::://///++++++++++++++++++////////////:::---. :/:-..--.
              -://:. ////////:::::::::/:/:::::::::::::::::::::::::::::::-:` `-/:--.
              -::-` `:///::-.`-::://///:::::::::::::::::::::::::::::::::::`   .::-.
               ``    `...``  ``://///////:::::::::::::::::::::::::///////+/-   `..
                                .:///////////:::::::::::::::::////////+oo+++/.
                                 `.://///+++///::::::::::::://///+++o+oo++o++/:.
                           ``...----::::::://+///:::::::://///+++++/////++++++/:-`
                        `.---:-::----::::::::://////::://///+oo+/:::::-:::::::::::-`
                      `.::::::::::::::::::::::-`...``````````:/::::::::::-----------`
                      -::::///:::::/::/:::::::.             `/////::::::::::::::----.`
                      .://////////:///:::::-.`               .://///////::::::::::---.
                       `.-://///////:::--.``                  `-:///////////::::::::-`
                           ````````                             `.-::///////::::::-.
                                                                    `````...```
"""