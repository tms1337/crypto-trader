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
    mode = sys.argv[2]

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
        "poloniex": poloniex_wrapper,
        "bittrex": bittrex_wrapper,
        "bitfinex": bitfinex_wrapper
    }

    wrapper_container = ExchangeWrapperContainer(wrappers)

    trading_currencies = ["ETH"]

    base_exchange = "poloniex"

    if mode == "test":
        short_sell_threshold = 0.02
        short_buy_threshold = 0.01
        short_security = 0.1

        short_eth_value = 0.1
        short_btc_value = 0.01
    else:
        short_sell_threshold = 0.02
        short_buy_threshold = 0.005
        short_security = 0.1

        short_eth_value = 6
        short_btc_value = 0.3

    short_percent_based_transaction_decider = PercentBasedTransactionDecider(currencies=trading_currencies,
                                                                             trading_currency=quote_currency,
                                                                             wrapper_container=wrapper_container,
                                                                             sell_threshold=short_sell_threshold,
                                                                             buy_threshold=short_buy_threshold,
                                                                             security_loss_threshold=short_security)

    short_fixed_volume_decider = FixedValueVolumeDecider(wrapper_container=wrapper_container,
                                                         values={"ETH": short_eth_value})

    short_fiat_transaction_decider = PercentBasedTransactionDecider(currencies=["BTC"],
                                                                    trading_currency="USD",
                                                                    wrapper_container=wrapper_container,
                                                                    sell_threshold=short_sell_threshold,
                                                                    buy_threshold=short_buy_threshold,
                                                                    security_loss_threshold=short_security)

    short_fiat_volume_decider = FixedValueVolumeDecider(wrapper_container=wrapper_container,
                                                        values={"BTC": short_btc_value})

    if mode == "test":
        long_sell_threshold = 0.04
        long_buy_threshold = 0.02
        long_security = 0.1

        long_eth_value = 0.1
        long_btc_value = 0.01
    else:
        long_sell_threshold = 0.04
        long_buy_threshold = 0.005
        long_security = 0.1

        long_eth_value = 6
        long_btc_value = 0.3

    long_percent_based_transaction_decider = PercentBasedTransactionDecider(currencies=trading_currencies,
                                                                            trading_currency=quote_currency,
                                                                            wrapper_container=wrapper_container,
                                                                            sell_threshold=long_sell_threshold,
                                                                            buy_threshold=long_buy_threshold,
                                                                            security_loss_threshold=long_security)

    long_fixed_volume_decider = FixedValueVolumeDecider(wrapper_container=wrapper_container,
                                                        values={"ETH": long_eth_value})

    long_fiat_transaction_decider = PercentBasedTransactionDecider(currencies=["BTC"],
                                                                    trading_currency="USD",
                                                                    wrapper_container=wrapper_container,
                                                                    sell_threshold=long_sell_threshold,
                                                                    buy_threshold=long_buy_threshold,
                                                                    security_loss_threshold=long_security)

    long_fiat_volume_decider = FixedValueVolumeDecider(wrapper_container=wrapper_container,
                                                        values={"BTC": long_btc_value})

    daemon = Daemon(wrapper_container=wrapper_container,
                    dt_seconds=dt,
                    transaction_deciders=[short_percent_based_transaction_decider,
                                          short_fiat_transaction_decider,
                                          long_percent_based_transaction_decider,
                                          long_fiat_transaction_decider],
                    volume_deciders=[short_fixed_volume_decider,
                                     short_fiat_volume_decider,
                                     long_fixed_volume_decider,
                                     long_fiat_volume_decider],
                    logger_name="app")

except Exception as ex:
    print("Error while initializing daemon and its parts"
          "\n\tError message: %s" % str(ex))

if daemon is not None:
    daemon.run()
