from trading.daemon import Daemon
from trading.deciders.decision import Decision, TransactionType
from trading.deciders.transaction.exchangediff import ExchangeDiffDecider, ExchangeDiffBackup
from trading.deciders.transaction.percentbased import PercentBasedTransactionDecider
from trading.deciders.transaction.simple import AlwaysBuyTransactionDecider
from trading.deciders.volume.fixedbalancepercentage import FixedBalancePercentageVolumeDecider
from trading.deciders.volume.fixedincome import FixedIncomeVolumeDecider
from trading.deciders.volume.simple import FixedValueVolumeDecider
from trading.exchange.base import ExchangeWrapper, ExchangeWrapperContainer
from trading.exchange.bitfinex.stats import BitfinexStatsProvider
from trading.exchange.bitfinex.trade import BitfinexTradeProvider
from trading.exchange.bittrex.stats import BittrexStatsProvider
from trading.exchange.bittrex.trade import BittrexTradeProvider
from trading.exchange.kraken.mocks import TradeProviderMock, StatsProviderMock

import sys

from trading.exchange.kraken.stats import KrakenStatsProvider
from trading.exchange.kraken.trade import KrakenTradeProvider
from trading.exchange.poloniex.stats import PoloniexStatsProvider
from trading.exchange.poloniex.trade import PoloniexTradeProvider

import logging

# create logger with 'spam_application'
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

daemon = None

try:
    quote_currency = "BTC"
    dt = 30
    key_directory = sys.argv[1]

    kraken_stats = KrakenStatsProvider()
    kraken_trader = KrakenTradeProvider(key_uri=("%s/kraken_key" % key_directory))

    kraken_wrapper = ExchangeWrapper(stats_provider=kraken_stats,
                                     trade_provider=kraken_trader,
                                     spending_factor=1)

    poloniex_stats = PoloniexStatsProvider()
    poloniex_trader = PoloniexTradeProvider(key_uri=("%s/poloniex_key" % key_directory))
    poloniex_wrapper = ExchangeWrapper(stats_provider=poloniex_stats,
                                       trade_provider=poloniex_trader,
                                       spending_factor=1)

    bittrex_stats = BittrexStatsProvider()
    bittrex_trader = BittrexTradeProvider(key_uri=("%s/bittrex_key" % key_directory))
    bittrex_wrapper = ExchangeWrapper(stats_provider=bittrex_stats,
                                      trade_provider=bittrex_trader,
                                      spending_factor=1)

    bitfinex_stats = BitfinexStatsProvider()
    bitfinex_trader = BitfinexTradeProvider(key_uri=("%s/bitfinex_key" % key_directory))
    bitfinex_wrapper = ExchangeWrapper(stats_provider=bitfinex_stats,
                                       trade_provider=bitfinex_trader,
                                       spending_factor=1)

    wrappers = {
        "kraken": kraken_wrapper,
    }

    wrapper_container = ExchangeWrapperContainer(wrappers)

    trading_currencies = ["ETH", "LTC", "DASH"]

    base_exchange = "kraken"

    sell_threshold = 0.01
    buy_threshold = 0.005
    security_loss = 0.05

    btc_value = 0.5

    euro_wrappers = {
        "kraken": bittrex_wrapper,
    }

    euro_wrapper_container = ExchangeWrapperContainer(wrappers=euro_wrappers)

    euro_transaction_decider = PercentBasedTransactionDecider(currencies=["BTC"],
                                                              trading_currency="USD",
                                                              wrapper_container=euro_wrapper_container,
                                                              sell_threshold=sell_threshold,
                                                              buy_threshold=buy_threshold,
                                                              security_loss_threshold=security_loss)

    euro_volume_decider = FixedValueVolumeDecider(wrapper_container=wrapper_container,
                                                  values={"BTC": btc_value})

    daemon = Daemon(wrapper_container=wrapper_container,
                    dt_seconds=dt,
                    transaction_deciders=[euro_transaction_decider],
                    volume_deciders=[euro_volume_decider],
                    logger_name="app")

except Exception as ex:
    print("Error while initializing daemon and its parts"
          "\n\tError message: %s" % str(ex))

if daemon is not None:
    daemon.run()
