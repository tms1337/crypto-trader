import logging
import sys

from bot.daemon import Daemon
from bot.exchange.bitfinex.trade import BitfinexTradeProvider
from bot.exchange.bittrex.stats import BittrexStatsProvider
from bot.exchange.bittrex.trade import BittrexTradeProvider
from bot.exchange.kraken.stats import KrakenStatsProvider
from bot.exchange.kraken.trade import KrakenTradeProvider
from bot.exchange.poloniex.stats import PoloniexStatsProvider
from bot.exchange.poloniex.trade import PoloniexTradeProvider
from bot.strategy.deciders.simple.base import SimpleCompositeDecider
from bot.strategy.deciders.simple.offer.exchangediff import ExchangeDiffOfferDecider
from bot.strategy.deciders.simple.offer.percentbased import PercentBasedOfferDecider
from bot.strategy.deciders.simple.volume.fixedvalue import FixedValueVolumeDecider
from bot.strategy.pipeline.block import Block
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

currencies = ["BTC"]
trading_currency = "USD"

daemon_dt = float(sys.argv[3])
providers_pause_dt = 0.1

keys_path = sys.argv[1]
btc_value = float(sys.argv[2])

stats_providers = {
    "poloniex": PoloniexStatsProvider(pause_dt=providers_pause_dt),
    "bittrex": BittrexStatsProvider(pause_dt=providers_pause_dt),
    # "bitfinex": BitfinexStatsProvider(),
    # "kraken": KrakenStatsProvider()
}
trade_providers = {
    "poloniex": PoloniexTradeProvider(key_uri=("%s/poloniex" % keys_path), pause_dt=providers_pause_dt),
    "bittrex": BittrexTradeProvider(key_uri=("%s/bittrex" % keys_path), pause_dt=providers_pause_dt),
    # "bitfinex": BitfinexTradeProvider(key_uri=("%s/bitfinex" % keys_path)),
    # "kraken": KrakenTradeProvider(key_uri=("%s/kraken" % keys_path))
}

informer = Informer(base_currency=trading_currency,
                    stats_providers=stats_providers,
                    trade_providers=trade_providers,
                    currencies=currencies)

short_percent_decider = SimpleCompositeDecider(trade_providers=trade_providers,
                                               offer_decider=PercentBasedOfferDecider(currencies=currencies,
                                                                                      buy_threshold=0.02,
                                                                                      sell_threshold=0.005,
                                                                                      security_loss_threshold=0.05,
                                                                                      trading_currency=trading_currency),
                                               volume_decider=FixedValueVolumeDecider(values={"BTC": 0.3}))

long_percent_decider = SimpleCompositeDecider(trade_providers=trade_providers,
                                              offer_decider=PercentBasedOfferDecider(currencies=currencies,
                                                                                     buy_threshold=0.02,
                                                                                     sell_threshold=0.01,
                                                                                     security_loss_threshold=0.05,
                                                                                     trading_currency=trading_currency),
                                              volume_decider=FixedValueVolumeDecider(values={"BTC": 0.3}))

diff_decider = SimpleCompositeDecider(trade_providers=trade_providers,
                                      offer_decider=ExchangeDiffOfferDecider(currencies=currencies,
                                                                             trading_currency=trading_currency),
                                      volume_decider=FixedValueVolumeDecider(values={"BTC": btc_value}))

# he's gonna kill you !!!
executor = TransactionExecutor(trade_providers=trade_providers)

block = Block(decider_pipeline=DeciderPipeline(deciders=[diff_decider]),
              informer=informer,
              transaction_executor=executor,
              monitors=[MongoBalanceMonitor(currencies=currencies,
                                            name="diff_bot")])

daemon = Daemon(blocks=[block],
                dt_seconds=daemon_dt)

if daemon is not None:
    daemon.run()
