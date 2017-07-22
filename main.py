import logging
import sys

from trading.daemon import Daemon
from trading.exchange.kraken.stats import KrakenStatsProvider
from trading.exchange.kraken.trade import KrakenTradeProvider
from trading.strategy.deciders.simple.base import SimpleCompositeDecider
from trading.strategy.deciders.simple.offer.percentbased import PercentBasedOfferDecider
from trading.strategy.deciders.simple.volume.fixedvalue import FixedValueVolumeDecider
from trading.strategy.pipeline.block import Block
from trading.strategy.pipeline.deciderpipeline import DeciderPipeline
from trading.strategy.pipeline.informer import Informer
from trading.strategy.pipeline.transactionexecutor import TransactionExecutor

logger = logging.getLogger('app')
logger.setLevel(logging.DEBUG)

# create file handler which logs even debug messages
fh = logging.FileHandler('debug.log')
fh.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)

# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - '
                              '%(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

currencies = ["ETH"]
trading_currency = "BTC"

stats_providers = {
    # "poloniex": PoloniexStatsProvider(),
    # "bittrex": BittrexStatsProvider(),
    # "bitfinex": BitfinexStatsProvider(),
    "kraken": KrakenStatsProvider()
}
trade_providers = {
    # "poloniex": PoloniexTradeProvider(key_uri="/home/faruk/Desktop/poloniex_key"),
    # "bittrex": BittrexTradeProvider(key_uri="/home/faruk/Desktop/bittrex_key"),
    # "bitfinex": BitfinexTradeProvider(key_uri="/home/faruk/Desktop/bitfinex_key"),
    "kraken": KrakenTradeProvider(key_uri="/home/faruk/Desktop/kraken_key")
}

informer = Informer(base_currency=trading_currency,
                    stats_providers=stats_providers,
                    currencies=currencies)

percent_decider = SimpleCompositeDecider(trade_providers=trade_providers,
                                         offer_decider=PercentBasedOfferDecider(currencies=currencies,
                                                                                buy_threshold=0.1,
                                                                                sell_threshold=0.1,
                                                                                security_loss_threshold=0.1,
                                                                                trading_currency=trading_currency),
                                         volume_decider=FixedValueVolumeDecider(values={"ETH": 0.1}))

# he's gonna kill you !!!
executor = TransactionExecutor(trade_providers=trade_providers)

block = Block(decider_pipeline=DeciderPipeline(deciders=[percent_decider]),
              informer=informer,
              transaction_executor=executor)

daemon = Daemon(blocks=[block],
                dt_seconds=15)


if daemon is not None:
    daemon.run()
