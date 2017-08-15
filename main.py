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

daemon_dt = float(sys.argv[2])
providers_pause_dt = 0.5

keys_path = sys.argv[1]

stats_providers = {
    # "poloniex": PoloniexStatsProvider(pause_dt=providers_pause_dt),
    "bittrex": BittrexStatsProvider(pause_dt=providers_pause_dt),
    # "bitfinex": BitfinexStatsProvider(),
    # "kraken": KrakenStatsProvider()
}
trade_providers = {
    # "poloniex": PoloniexTradeProvider(key_uri=("%s/poloniex" % keys_path), pause_dt=providers_pause_dt),
    "bittrex": BittrexTradeProvider(key_uri=("%s/bittrex" % keys_path), pause_dt=providers_pause_dt),
    # "bitfinex": BitfinexTradeProvider(key_uri=("%s/bitfinex" % keys_path)),
    # "kraken": KrakenTradeProvider(key_uri=("%s/kraken" % keys_path))
}

currencies_for_crypto = ["ETH", "DASH", "NEO", "QTUM"]
trading_currency_for_crypto = "BTC"

crypto_informer = Informer(base_currency=trading_currency_for_crypto,
                           stats_providers=stats_providers,
                           trade_providers=trade_providers,
                           currencies=currencies_for_crypto)

crypto_values = {"ETH": 10, "DASH": 8, "NEO": 50, "QTUM": 150}
short_percent_crypto_decider = SimpleCompositeDecider(trade_providers=trade_providers,
                                                      offer_decider=PercentBasedOfferDecider(
                                                          currencies=currencies_for_crypto,
                                                          buy_threshold=0.005,
                                                          sell_threshold=0.01,
                                                          security_loss_threshold=0.2,
                                                          trading_currency=trading_currency_for_crypto),
                                                      volume_decider=FixedValueVolumeDecider(
                                                          values=crypto_values))

long_percent_crypto_decider = SimpleCompositeDecider(trade_providers=trade_providers,
                                                     offer_decider=PercentBasedOfferDecider(
                                                         currencies=currencies_for_crypto,
                                                         buy_threshold=0.01,
                                                         sell_threshold=0.05,
                                                         security_loss_threshold=0.2,
                                                         trading_currency=trading_currency_for_crypto),
                                                     volume_decider=FixedValueVolumeDecider(
                                                         values=crypto_values))

# he's gonna kill you !!!
executor = TransactionExecutor(trade_providers=trade_providers)

crypto_block = Block(decider_pipeline=DeciderPipeline(deciders=[short_percent_crypto_decider,
                                                                long_percent_crypto_decider]),
                     informer=crypto_informer,
                     transaction_executor=executor,
                     monitors=[MongoBalanceMonitor(currencies=["ETH", "DASH", "NEO", "USD", "QTUM"],
                                                   name="weekly_test_004")])

daemon = Daemon(blocks=[crypto_block],
                dt_seconds=daemon_dt)

if daemon is not None:
    daemon.run()
