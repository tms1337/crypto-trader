import logging
import sys

from bot.daemon import Daemon
from bot.exchange.poloniex.stats import PoloniexStatsProvider
from bot.exchange.poloniex.trade import PoloniexTradeProvider
from bot.strategy.deciders.smart.discrete_levels import DiscreteLevelsDecider
from bot.strategy.pipeline.block import Block
from bot.strategy.pipeline.deciderpipeline import DeciderPipeline
from bot.strategy.pipeline.informer import Informer
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
providers_pause_dt = 0.2

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

crypto_informer = Informer(base_currency=trading_currency_for_crypto,
                           stats_providers=stats_providers,
                           trade_providers=trade_providers,
                           currencies=currencies_for_crypto,
                           historic_n=50,
                           interval=1800)


decider = DiscreteLevelsDecider(trade_providers=trade_providers,
                                threshold=0.05,
                                trends_len=4,
                                default_position=True)

executor = TransactionExecutor(trade_providers=trade_providers)

crypto_block = Block(decider_pipeline=DeciderPipeline(deciders=[decider]),
                     informer=crypto_informer,
                     transaction_executor=executor,
                     monitors=[])

daemon = Daemon(blocks=[crypto_block],
                dt_seconds=daemon_dt)

if daemon is not None:
    while True:
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